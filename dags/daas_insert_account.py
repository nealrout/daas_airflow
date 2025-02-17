from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
import json
import base64

SOLR_COLLECTION_ACCOUNT = "account"
SOLR_COLLECTION_FACILITY = "facility"
SOLR_COLLECTION_ASSET = "asset"
SOLR_COLLECTION_SERVICE = "service"

PAYLOAD = [
    {
        "acct_nbr": "INT_ACCT_NBR_01",
        "acct_code": "INT_US_ACCT_01",
        "acct_name": "Integration account 01"
    },
    {
        "acct_nbr": "INT_ACCT_NBR_02",
        "acct_code": "INT_US_ACCT_02",
        "acct_name": "Integration account 02"
    }
]

with DAG(
    dag_id="daas_insert_account",
    schedule_interval=None,  # Manual trigger
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Authenticate and get token
    trigger_cleanup = TriggerDagRunOperator(
        task_id="trigger_daas_cleanup",
        trigger_dag_id="daas_cleanup",  
        wait_for_completion=True,  # Wait until cleanup completes before continuing
    )

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
                print(f"✅ Extracted Token: {access_token}") 
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
    push_account_upsert = SimpleHttpOperator(
        task_id="push_account_upsert",
        http_conn_id="daas_api_account", 
        endpoint="/api/account/db/upsert/?facility=ALL",
        method="POST",
        data=json.dumps(PAYLOAD),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ ti.xcom_pull(task_ids='extract_token', key='access_token') }}"
        },
        log_response=True,
    )

    # Define DAG Task Flow
    trigger_cleanup >> authenticate >> extract_token_task >> push_account_upsert
