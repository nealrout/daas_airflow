import os
import json
from airflow.models import Variable # type: ignore
from airflow import DAG # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from airflow.operators.trigger_dagrun import TriggerDagRunOperator # type: ignore
from airflow.utils.dates import days_ago # type: ignore

# Path to the JSON config file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "domains_insert_config.json")

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
    dag_id="wrapper_daas_insert",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:
    # Task to delete all test data before starting.
    trigger_cleanup_task = TriggerDagRunOperator(
        task_id="daas_cleanup",
        trigger_dag_id="daas_cleanup",  
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "account"
    set_domain_account_task = PythonOperator(
        task_id="set_domain_account",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "account"},
    )

    # Trigger `account` DAG first and wait for completion
    trigger_account_task = TriggerDagRunOperator(
        task_id="daas_insert_generic_account",
        trigger_dag_id="daas_insert_generic",
        conf={"DOMAIN": "account"},
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "facility"
    set_domain_facility_task = PythonOperator(
        task_id="set_domain_facility",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "facility"},
    )

    # Trigger `facility` DAG only after `account` DAG finishes
    trigger_facility_task = TriggerDagRunOperator(
        task_id="daas_insert_generic_facility",
        trigger_dag_id="daas_insert_generic",
        conf={"DOMAIN": "facility"},
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "asset"
    set_domain_asset_task = PythonOperator(
        task_id="set_domain_asset",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "asset"},
    )

    # Trigger `asset` DAG only after `facility` DAG finishes
    trigger_asset_task = TriggerDagRunOperator(
        task_id="daas_insert_generic_asset",
        trigger_dag_id="daas_insert_generic",
        conf={"DOMAIN": "asset"},
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "service"
    set_domain_service_task = PythonOperator(
        task_id="set_domain_service",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "service"},
    )

    # Trigger `service` DAG only after `asset` DAG finishes
    trigger_service_task = TriggerDagRunOperator(
        task_id="daas_insert_generic_service",
        trigger_dag_id="daas_insert_generic",
        conf={"DOMAIN": "service"},
        wait_for_completion=True,  
    )

    # # Trigger daas_add_user_facility
    # trigger_add_user_facility = TriggerDagRunOperator(
    #     task_id="daas_add_user_facility",
    #     trigger_dag_id="daas_add_user_facility",
    #     wait_for_completion=True,  
    # )

    (
        trigger_cleanup_task 
        >> set_domain_account_task >> trigger_account_task 
        >> set_domain_facility_task >> trigger_facility_task 
        >> set_domain_asset_task >> trigger_asset_task 
        >> set_domain_service_task >> trigger_service_task
    )
