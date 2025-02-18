from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.time_delta import TimeDeltaSensorAsync
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models import Variable
import json

def load_constants():
    """Loads domain-specific constants at execution time but allows top-level references."""
    DOMAIN = Variable.get("DOMAIN", default_var="")

    return {
        "DOMAIN": DOMAIN,
        "DOMAIN_SOLR_KEY": Variable.get(f"{DOMAIN}_DOMAIN_SOLR_KEY", default_var=""),
        "DOMAIN_SOLR_COLLECTION": Variable.get(f"{DOMAIN}_DOMAIN_SOLR_COLLECTION", default_var=""),
        "UPSERT_PAYLOAD": json.loads(Variable.get(f"{DOMAIN}_UPSERT_PAYLOAD", default_var="[]")),
        "SOLR_EXPECTED_RECORDS": json.loads(Variable.get(f"{DOMAIN}_SOLR_EXPECTED_RECORDS", default_var="{}"))
    }

# Load constants ONCE when DAG is parsed
CONSTANTS = load_constants()
DOMAIN = CONSTANTS["DOMAIN"]
DOMAIN_SOLR_KEY = CONSTANTS["DOMAIN_SOLR_KEY"]
DOMAIN_SOLR_COLLECTION = CONSTANTS["DOMAIN_SOLR_COLLECTION"]
UPSERT_PAYLOAD = CONSTANTS["UPSERT_PAYLOAD"]
SOLR_EXPECTED_RECORDS = CONSTANTS["SOLR_EXPECTED_RECORDS"]

with DAG(
    dag_id="daas_insert_generic",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:
    
    def print_constant_values():
        print (f"💡DOMAIN:💡 {DOMAIN}")
        print (f"💡DOMAIN_SOLR_KEY:💡 {DOMAIN_SOLR_KEY}")
        print (f"💡DOMAIN_SOLR_COLLECTION:💡 {DOMAIN_SOLR_COLLECTION}")
        print (f"💡UPSERT_PAYLOAD:💡 {UPSERT_PAYLOAD}")
        print (f"💡SOLR_EXPECTED_RECORDS:💡 {SOLR_EXPECTED_RECORDS}")

    print_constants = PythonOperator(
        task_id="print_constants",
        python_callable=print_constant_values,
        provide_context=True,
    )

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
        task_id=f"push_generic_upsert",
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

        found_records = {doc.get(primary_key, f"unknown_{i}"): doc for i, doc in enumerate(docs)}

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

    print_constants >> authenticate >> extract_token_task >> push_domain_upsert >> wait_task >> query_solr >> validate_solr_task
