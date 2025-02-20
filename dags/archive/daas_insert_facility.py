from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.time_delta import TimeDeltaSensorAsync
from airflow.utils.dates import days_ago
from datetime import timedelta
import json
DOMAIN = "facility"
DOMAIN_SOLR_KEY = "fac_nbr"
DOMAIN_SOLR_COLLECTION = "facility"

UPSERT_PAYLOAD = [
    {
        "acct_nbr": "INT_ACCT_NBR_01",
        "fac_code": "INT_US_TEST_01",
        "fac_name": "Integration facility 01",
        "fac_nbr": "INT_FAC_NBR_01"
    },
    {
        "acct_nbr": "INT_ACCT_NBR_02",
        "fac_code": "INT_US_TEST_02",
        "fac_name": "Integration facility 02",
        "fac_nbr": "INT_FAC_NBR_02"
    }
]

SOLR_EXPECTED_RECORDS = {
    "INT_FAC_NBR_01": {
        "acct_nbr": "INT_ACCT_NBR_01",
        "fac_code": "INT_US_TEST_01",
        "fac_name": "Integration facility 01"
    },
    "INT_FAC_NBR_02": {
        "acct_nbr": "INT_ACCT_NBR_02",
        "fac_code": "INT_US_TEST_02",
        "fac_name": "Integration facility 02"
    }
}

with DAG(
    dag_id=f"daas_insert_{DOMAIN}",
    schedule_interval=None,  # Manual trigger
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Authenticate and get token
    # trigger_cleanup = TriggerDagRunOperator(
    #     task_id="trigger_daas_cleanup",
    #     trigger_dag_id="daas_cleanup",  
    #     wait_for_completion=True,  # Wait until cleanup completes before continuing
    # )

    authenticate = SimpleHttpOperator(
        task_id="get_auth_token",
        http_conn_id="daas_auth",  # Ensure this connection exists in Airflow
        endpoint="/api/auth/login/",
        method="POST",
        headers={"Content-Type": "application/json"},
        response_check=lambda response: response.status_code == 200,
        log_response=True,
        do_xcom_push=True,  # Store response in XCom
    )
    # Extract Token from Response
    def extract_token(**kwargs):
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
    # Make API Request Using Extracted Token
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
        endpoint=f"/solr/{DOMAIN_SOLR_COLLECTION}/select?q={DOMAIN_SOLR_KEY}:INT_*",
        method="GET",
        log_response=True,
        do_xcom_push=True,  
    )

    def validate_solr_response(primary_key="", **kwargs):
        import json

        ti = kwargs["ti"]
        response = ti.xcom_pull(task_ids="query_solr")  
        response_json = json.loads(response)

        docs = response_json.get("response", {}).get("docs", [])

        # Ensure primary_key exists in every doc, fallback to index-based key if missing
        found_records = {
            doc.get(primary_key, f"unknown_{i}"): doc
            for i, doc in enumerate(docs)
        }

        print("✅ Found records:", found_records)
        
        # Example validation: Check if expected records exist
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

    # Define DAG Task Flow
    authenticate >> extract_token_task >> push_domain_upsert >> wait_task >> query_solr  >> validate_solr_task
