from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import json


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
    dag_id="authenticate_and_post",
    schedule_interval=None,  # Manual trigger
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Cleanup data
    clean_query = PostgresOperator(
        task_id="clean_integration_data",
        postgres_conn_id="postgres_us_int_daas",  
        sql="CALL clean_integration_data();",  
    )

    # Authenticate and get token
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
    push_data = SimpleHttpOperator(
        task_id="post_with_auth",
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
    clean_query >> authenticate >> extract_token_task >> push_data
