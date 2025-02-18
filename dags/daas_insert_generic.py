from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.time_delta import TimeDeltaSensorAsync
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models import Variable
import json
from airflow.models import Variable

default_variables = {
    "DOMAIN": "facility",
    "DOMAIN_SOLR_KEY": "fac_nbr",
    "DOMAIN_SOLR_COLLECTION": "facility",
    "UPSERT_PAYLOAD": "",
    "SOLR_EXPECTED_RECORDS":""
}
# Ensure all required variables exist in Airflow
for key, value in default_variables.items():
    if not Variable.get(key, default_var=None):
        Variable.set(key, value)

# Retrieve variables from Airflow Variables
DOMAIN = Variable.get("DOMAIN")
DOMAIN_SOLR_KEY = Variable.get("DOMAIN_SOLR_KEY")
DOMAIN_SOLR_COLLECTION = Variable.get("DOMAIN_SOLR_COLLECTION")
UPSERT_PAYLOAD = json.loads(Variable.get("UPSERT_PAYLOAD"))
SOLR_EXPECTED_RECORDS = json.loads(Variable.get("SOLR_EXPECTED_RECORDS"))

with DAG(
    dag_id="daas_insert_generic",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Authenticate and get token
    authenticate = SimpleHttpOperator(
        task_id="get_auth_token",
        http_conn_id="daas_auth",
        endpoint="/api/auth/login/",
        method="POST",
        headers={"Content-Type": "application/json"},
        response_check=lambda response: response.status_code == 200,
        log_response=True,
        do_xcom_push=True,
    )

    def extract_token(**kwargs):
        """Extract and store auth token from API response"""
        ti = kwargs["ti"]
        response = ti.xcom_pull(task_ids="get_auth_token")
        if response:
            response_json = json.loads(response)
            access_token = response_json.get("access")
            if access_token:
                ti.xcom_push(key="access_token", value=access_token)
                print(f"Extracted Token: {access_token}")
            else:
                raise ValueError("❌ No 'access' token found in response!")
        else:
            raise ValueError("❌ Authentication response is empty!")

    extract_token_task = PythonOperator(
        task_id="extract_token",
        python_callable=extract_token,
        provide_context=True,
    )

    push_domain_upsert = SimpleHttpOperator(
        task_id=f"push_{DOMAIN}_upsert",
        http_conn_id=f"daas_api_{DOMAIN}",
        endpoint=f"/api/{DOMAIN}/db/upsert/?facility=ALL",
        method="POST",
        data=json.dumps(UPSERT_PAYLOAD),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ ti.xcom_pull(task_ids='extract_token', key='access_token') }}"
        },
        log_response=True,
    )

    query_solr = SimpleHttpOperator(
        task_id="query_solr",
        http_conn_id="solr_integration",
        endpoint=f"solr/{DOMAIN_SOLR_COLLECTION}/select?q={DOMAIN_SOLR_KEY}:INT_*",
        method="GET",
        log_response=True,
        do_xcom_push=True,
    )

    def validate_solr_response(primary_key="", **kwargs):
        """Validate Solr response against expected records"""
        ti = kwargs["ti"]
        response = ti.xcom_pull(task_ids="query_solr")
        response_json = json.loads(response)

        docs = response_json.get("response", {}).get("docs", [])

        found_records = {
            doc.get(primary_key, f"unknown_{i}"): doc
            for i, doc in enumerate(docs)
        }

        print("✅ Found records:", found_records)
        
        for nbr, expected_values in SOLR_EXPECTED_RECORDS.items():
            if nbr not in found_records:
                raise ValueError(f"❌ Missing expected record: {nbr}")
            if not all(item in found_records[nbr].items() for item in expected_values.items()):
                raise ValueError(f"❌ Data mismatch for {nbr}: {found_records[nbr]} != {expected_values}")

        print("✅ All expected records were found in Solr!")

    validate_solr_task = PythonOperator(
        task_id="validate_solr_response",
        python_callable=validate_solr_response,
        op_kwargs={"primary_key": DOMAIN_SOLR_KEY},
        provide_context=True,
    )

    wait_task = TimeDeltaSensorAsync(
        task_id="wait_15_seconds",
        delta=timedelta(seconds=15),
    )

    authenticate >> extract_token_task >> push_domain_upsert >> wait_task >> query_solr >> validate_solr_task
