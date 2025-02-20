import os
import json
from airflow.models import Variable # type: ignore
from airflow import DAG # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from airflow.operators.trigger_dagrun import TriggerDagRunOperator # type: ignore
from airflow.utils.dates import days_ago # type: ignore

# Path to the JSON config file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "domains_search_config.json")

# Load domain configurations from the JSON file
with open(CONFIG_FILE_PATH, "r") as file:
    domains = json.load(file)

# Store domain parameters in Airflow Variables
for domain, params in domains.items():
    for key, value in params.items():
        Variable.set(f"{domain}_{key}", json.dumps(value))

def set_domain_variable(domain):
    """Set DOMAIN variable before triggering the DAG."""
    Variable.set("DOMAIN", domain)
    print(f"💡Set DOMAIN to: {domain}")

# Define DAG
with DAG(
    dag_id="wrapper_daas_search",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Task to set DOMAIN for "account"
    set_domain_account = PythonOperator(
        task_id="set_domain_account",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "account"},
    )

    # Trigger `account` DAG first and wait for completion
    trigger_account = TriggerDagRunOperator(
        task_id="daas_search_generic_account",
        trigger_dag_id="daas_search_generic",
        conf={"DOMAIN": "account"},
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "facility"
    set_domain_facility = PythonOperator(
        task_id="set_domain_facility",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "facility"},
    )

    # Trigger `facility` DAG only after `account` DAG finishes
    trigger_facility = TriggerDagRunOperator(
        task_id="daas_search_generic_facility",
        trigger_dag_id="daas_search_generic",
        conf={"DOMAIN": "facility"},
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "asset"
    set_domain_asset = PythonOperator(
        task_id="set_domain_asset",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "asset"},
    )

    # Trigger `asset` DAG only after `facility` DAG finishes
    trigger_asset = TriggerDagRunOperator(
        task_id="daas_search_generic_asset",
        trigger_dag_id="daas_search_generic",
        conf={"DOMAIN": "asset"},
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "service"
    set_domain_service = PythonOperator(
        task_id="set_domain_service",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "service"},
    )

    # Trigger `service` DAG only after `asset` DAG finishes
    trigger_service = TriggerDagRunOperator(
        task_id="daas_search_generic_service",
        trigger_dag_id="daas_search_generic",
        conf={"DOMAIN": "service"},
        wait_for_completion=True,  
    )

    # Ensure sequential execution: set DOMAIN → trigger DAG → set DOMAIN → trigger DAG
    (
        set_domain_account >> trigger_account 
        >> set_domain_facility >> trigger_facility 
        >> set_domain_asset >> trigger_asset 
        >> set_domain_service >> trigger_service
    )
