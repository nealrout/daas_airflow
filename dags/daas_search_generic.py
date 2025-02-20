from airflow import DAG # type: ignore
from airflow.providers.http.operators.http import SimpleHttpOperator # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from airflow.sensors.time_delta import TimeDeltaSensorAsync # type: ignore
from airflow.utils.dates import days_ago # type: ignore
from datetime import timedelta
from airflow.models import Variable # type: ignore
import json

def load_constants():
    """Loads domain-specific constants at execution time but allows top-level references."""
    DOMAIN = Variable.get("DOMAIN", default_var="account")

    return {
        "DOMAIN": DOMAIN,
        "DOMAIN_KEY": Variable.get(f"{DOMAIN}_DOMAIN_KEY", default_var=""),
        "API_POST_DB_SEARCH": json.loads(Variable.get(f"{DOMAIN}_API_POST_DB_SEARCH", default_var="{}")),
        "API_POST_DB_SEARCH_RESULTS": json.loads(Variable.get(f"{DOMAIN}_API_POST_DB_SEARCH_RESULTS", default_var="{}")),
        "API_POST_CACHE_SEARCH": json.loads(Variable.get(f"{DOMAIN}_API_POST_CACHE_SEARCH", default_var="{}")),
        "API_POST_CACHE_SEARCH_RESULTS": json.loads(Variable.get(f"{DOMAIN}_API_POST_CACHE_SEARCH_RESULTS", default_var="{}"))
    }

# Load constants ONCE when DAG is parsed
CONSTANTS = load_constants()
DOMAIN = CONSTANTS["DOMAIN"]
DOMAIN_KEY = CONSTANTS["DOMAIN_KEY"]
API_POST_DB_SEARCH = CONSTANTS["API_POST_DB_SEARCH"]
API_POST_DB_SEARCH_RESULTS = CONSTANTS["API_POST_DB_SEARCH_RESULTS"]
API_POST_CACHE_SEARCH = CONSTANTS["API_POST_CACHE_SEARCH"]
API_POST_CACHE_SEARCH_RESULTS = CONSTANTS["API_POST_CACHE_SEARCH_RESULTS"]

with DAG(
    dag_id="daas_search_generic",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:
    
    def print_constant_values():
        print (f"💡DOMAIN:💡 {DOMAIN}")
        print (f"💡DOMAIN_KEY:💡 {DOMAIN_KEY}")
        print (f"💡API_POST_DB_SEARCH:💡 {API_POST_DB_SEARCH}")
        print (f"💡API_POST_DB_SEARCH_RESULTS:💡 {API_POST_DB_SEARCH_RESULTS}")

    print_constants_task = PythonOperator(
        task_id="print_constants",
        python_callable=print_constant_values,
        provide_context=True,
    )

    authenticate_task = SimpleHttpOperator(
        task_id="get_auth_token",
        http_conn_id="daas_auth",
        endpoint="/api/auth/login/",
        method="POST",
        headers={"Content-Type": "application/json"},
        response_check=lambda response: response.status_code == 200,
        log_response=True,
        do_xcom_push=True,
    )

    def extract_token_func(**kwargs):
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
        python_callable=extract_token_func,
        provide_context=True,
    )

    call_api_get_all_task = SimpleHttpOperator(
        task_id=f"call_api_get_all",
        http_conn_id=f"daas_api_{DOMAIN}",
        endpoint=f"/api/{DOMAIN}/db/?facility=ALL",
        method="GET",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ ti.xcom_pull(task_ids='extract_token', key='access_token') }}"
        },
        response_filter=lambda response: response.text,
        log_response=True,
        do_xcom_push=True,
    )

    def validate_count_func(**kwargs):
        ti = kwargs['ti']
        response = ti.xcom_pull(task_ids='call_api_get_all')

        if not response:
            raise ValueError("No response received from API.")
        try:
            data = json.loads(response)  # Parse JSON string
            count = data.get("count", 0)  # Default to 0 if missing
            
            if count <= 0:
                raise ValueError(f"Invalid count value: {count}. Expected count > 0.")
            
            print(f"✅ Count check passed: {count} records found.")
        
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON response.")

    api_get_all_check_count_task = PythonOperator(
        task_id='validate_count',
        python_callable=validate_count_func,
        provide_context=True,
    )

    call_api_post_db_search_task = SimpleHttpOperator(
        task_id=f"call_api_post_db_search",
        http_conn_id=f"daas_api_{DOMAIN}",
        endpoint=f"/api/{DOMAIN}/db/?facility=ALL",
        method="POST",
        data=json.dumps(API_POST_DB_SEARCH),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ ti.xcom_pull(task_ids='extract_token', key='access_token') }}"
        },
        response_filter=lambda response: response.text,
        log_response=True,
        do_xcom_push=True,
    )

    def validate_db_response_func(primary_key="", **kwargs):
        """Validate api post search response against expected records"""
        ti = kwargs["ti"]
        response = ti.xcom_pull(task_ids="call_api_post_db_search")
        response_json = json.loads(response)

         #Convert response list into a dictionary keyed by the primary key
        found_records = {str(record.get(primary_key)): record for record in response_json}

        print("✅ Found records:", found_records)

        for nbr, expected_values in API_POST_DB_SEARCH_RESULTS.items():
            if nbr not in found_records:
                raise ValueError(f"❌ Missing expected record: {nbr}")
            if not all(item in found_records[nbr].items() for item in expected_values.items()):
                raise ValueError(f"❌ Data mismatch for {nbr}: {found_records[nbr]} != {expected_values}")

        print("✅ All expected records were found")

    validate_db_response_task = PythonOperator(
        task_id="validate_db_response",
        python_callable=validate_db_response_func,
        op_kwargs={"primary_key": DOMAIN_KEY},
        provide_context=True,
    )

    call_api_post_cache_search_task = SimpleHttpOperator(
        task_id=f"call_api_post_cache_search",
        http_conn_id=f"daas_api_{DOMAIN}",
        endpoint=f"/api/{DOMAIN}/cache/query?facility=ALL",
        method="POST",
        data=json.dumps(API_POST_CACHE_SEARCH),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ ti.xcom_pull(task_ids='extract_token', key='access_token') }}"
        },
        log_response=True,
    )

    def validate_solr_response_func(primary_key="", **kwargs):
        """Validate Solr response against expected records"""
        ti = kwargs["ti"]
        response = ti.xcom_pull(task_ids="call_api_post_cache_search")
        response_json = json.loads(response)

        docs = response_json.get("response", {}).get("docs", [])

        found_records = {doc.get(primary_key, f"unknown_{i}"): doc for i, doc in enumerate(docs)}

        print("✅ Found records:", found_records)

        for nbr, expected_values in API_POST_CACHE_SEARCH_RESULTS.items():
            if nbr not in found_records:
                raise ValueError(f"❌ Missing expected record: {nbr}")
            if not all(item in found_records[nbr].items() for item in expected_values.items()):
                raise ValueError(f"❌ Data mismatch for {nbr}: {found_records[nbr]} != {expected_values}")

        print("✅ All expected records were found in Solr!")

    validate_solr_response_task = PythonOperator(
        task_id="validate_solr_response",
        python_callable=validate_solr_response_func,
        op_kwargs={"primary_key": DOMAIN_KEY},
        provide_context=True,
    )

    (
        print_constants_task >> authenticate_task >> extract_token_task 
        >> call_api_get_all_task >> api_get_all_check_count_task 
        >> call_api_post_db_search_task >> validate_db_response_task 
        >> call_api_post_cache_search_task >> validate_solr_response_task
    )
