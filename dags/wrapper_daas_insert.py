import json
from airflow.models import Variable # type: ignore
from airflow import DAG # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from airflow.operators.trigger_dagrun import TriggerDagRunOperator # type: ignore
from airflow.utils.dates import days_ago # type: ignore

# Define parameters for each domain
domains = {
    "account": {
        "DOMAIN": "account",
        "DOMAIN_SOLR_KEY": "account_nbr",
        "DOMAIN_SOLR_COLLECTION": "account",
        "UPSERT_PAYLOAD": json.dumps([
            {
                "account_nbr": "INT_account_NBR_01",
                "account_code": "INT_US_account_01",
                "account_name": "Integration account 01"
            },
            {
                "account_nbr": "INT_account_NBR_02",
                "account_code": "INT_US_account_02",
                "account_name": "Integration account 02"
            }
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_account_NBR_01": {
                "account_code": "INT_US_account_01",
                "account_name": "Integration account 01"
            },
            "INT_account_NBR_02": {
                "account_code": "INT_US_account_02",
                "account_name": "Integration account 02"
            }
        })
    },
    "facility": {
        "DOMAIN": "facility",
        "DOMAIN_SOLR_KEY": "facility_nbr",
        "DOMAIN_SOLR_COLLECTION": "facility",
        "UPSERT_PAYLOAD": json.dumps([
            {
                "account_nbr": "INT_account_NBR_01",
                "facility_code": "INT_US_TEST_01",
                "facility_name": "Integration facility 01",
                "facility_nbr": "INT_facility_NBR_01"
            },
            {
                "account_nbr": "INT_account_NBR_02",
                "facility_code": "INT_US_TEST_02",
                "facility_name": "Integration facility 02",
                "facility_nbr": "INT_facility_NBR_02"
            }
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_facility_NBR_01": {
                "account_nbr": "INT_account_NBR_01",
                "facility_code": "INT_US_TEST_01",
                "facility_name": "Integration facility 01"
            },
            "INT_facility_NBR_02": {
                "account_nbr": "INT_account_NBR_02",
                "facility_code": "INT_US_TEST_02",
                "facility_name": "Integration facility 02"
            }
        })
    },
    "asset": {
        "DOMAIN": "asset",
        "DOMAIN_SOLR_KEY": "asset_nbr",
        "DOMAIN_SOLR_COLLECTION": "asset",
        "UPSERT_PAYLOAD": json.dumps([
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"sys_id": "INT_system_01",
				"asset_code": "INT_asset_code_01",
				"status_code": "up"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"sys_id": "INT_system_02",
				"asset_code": "INT_asset_code_02",
				"status_code": "down"
			},
			{
				"account_nbr": "INT_account_NBR_02",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"sys_id": "INT_system_03",
				"asset_code": "INT_asset_code_03",
				"status_code": "up"
			},
			{
				"account_nbr": "INT_account_NBR_02",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"sys_id": "INT_system_04",
				"asset_code": "INT_asset_code_04",
				"status_code": "down"
			}
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_ASSET_NBR_01": {
                "account_nbr": "INT_account_NBR_01",
                "facility_nbr": "INT_facility_NBR_01",
                "sys_id": "INT_system_01",
				"asset_code": "INT_asset_code_01",
				"status_code": "up"
            },
            "INT_ASSET_NBR_02": {
                "account_nbr": "INT_account_NBR_01",
                "facility_nbr": "INT_facility_NBR_01",
                "sys_id": "INT_system_02",
				"asset_code": "INT_asset_code_02",
				"status_code": "down"
            },
            "INT_ASSET_NBR_03": {
                "account_nbr": "INT_account_NBR_02",
                "facility_nbr": "INT_facility_NBR_02",
                "sys_id": "INT_system_03",
				"asset_code": "INT_asset_code_03",
				"status_code": "up"
            },
            "INT_ASSET_NBR_04": {
                "account_nbr": "INT_account_NBR_02",
                "facility_nbr": "INT_facility_NBR_02",
                "sys_id": "INT_system_04",
				"asset_code": "INT_asset_code_04",
				"status_code": "down"
            }
        })
    },
    "service": {
        "DOMAIN": "service",
        "DOMAIN_SOLR_KEY": "service_nbr",
        "DOMAIN_SOLR_COLLECTION": "service",
        "UPSERT_PAYLOAD": json.dumps([
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_nbr": "INT_INT_service_NBR_001",
				"service_code": "INT_service_001",
				"service_name": "Integration Service Name 001",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_nbr": "INT_INT_service_NBR_002",
				"service_code": "INT_service_002",
				"service_name": "Integration Service Name 002",
				"status_code": "close"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_nbr": "INT_INT_service_NBR_003",
				"service_code": "INT_service_003",
				"service_name": "Integration Service Name 003",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_nbr": "INT_INT_service_NBR_004",
				"service_code": "INT_service_004",
				"service_name": "Integration Service Name 004",
				"status_code": "close"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_nbr": "INT_INT_service_NBR_005",
				"service_code": "INT_service_005",
				"service_name": "Integration Service Name 005",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_nbr": "INT_INT_service_NBR_006",
				"service_code": "INT_service_006",
				"service_name": "Integration Service Name 006",
				"status_code": "close"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_nbr": "INT_INT_service_NBR_007",
				"service_code": "INT_service_007",
				"service_name": "Integration Service Name 007",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_nbr": "INT_INT_service_NBR_008",
				"service_code": "INT_service_008",
				"service_name": "Integration Service Name 008",
				"status_code": "close"
			}
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_INT_service_NBR_001": {
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_code": "INT_service_001",
				"service_name": "Integration Service Name 001",
				"status_code": "open"
            },
            "INT_INT_service_NBR_002": {
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_code": "INT_service_002",
				"service_name": "Integration Service Name 002",
				"status_code": "close"
            },
            "INT_INT_service_NBR_003": {
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_code": "INT_service_003",
				"service_name": "Integration Service Name 003",
				"status_code": "open"
            },
            "INT_INT_service_NBR_004": {
				"account_nbr": "INT_account_NBR_01",
				"facility_nbr": "INT_facility_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_code": "INT_service_004",
				"service_name": "Integration Service Name 004",
				"status_code": "close"
            },
            "INT_INT_service_NBR_005": {
				"account_nbr": "INT_account_NBR_02",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_code": "INT_service_005",
				"service_name": "Integration Service Name 005",
				"status_code": "open"
            },
            "INT_INT_service_NBR_006": {
				"account_nbr": "INT_account_NBR_02",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_code": "INT_service_006",
				"service_name": "Integration Service Name 006",
				"status_code": "close"
            },
            "INT_INT_service_NBR_007": {
				"account_nbr": "INT_account_NBR_02",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_code": "INT_service_007",
				"service_name": "Integration Service Name 007",
				"status_code": "open"
            },
            "INT_INT_service_NBR_008": {
				"account_nbr": "INT_account_NBR_02",
				"facility_nbr": "INT_facility_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_code": "INT_service_008",
				"service_name": "Integration Service Name 008",
				"status_code": "close"
            }
        })
    }
}

# Store domain parameters in Airflow Variables
for domain, params in domains.items():
    for key, value in params.items():
        Variable.set(f"{domain}_{key}", value)  

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
    trigger_cleanup = TriggerDagRunOperator(
        task_id="trigger_daas_cleanup",
        trigger_dag_id="daas_cleanup",  
        wait_for_completion=True,  
    )

    # Task to set DOMAIN for "account"
    set_domain_account = PythonOperator(
        task_id="set_domain_account",
        python_callable=set_domain_variable,
        op_kwargs={"domain": "account"},
    )

    # Trigger `account` DAG first and wait for completion
    trigger_account = TriggerDagRunOperator(
        task_id="trigger_child_dag_account",
        trigger_dag_id="daas_insert_generic",
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
        task_id="trigger_child_dag_facility",
        trigger_dag_id="daas_insert_generic",
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
        task_id="trigger_child_dag_asset",
        trigger_dag_id="daas_insert_generic",
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
        task_id="trigger_child_dag_service",
        trigger_dag_id="daas_insert_generic",
        conf={"DOMAIN": "service"},
        wait_for_completion=True,  
    )

    # Ensure sequential execution: set DOMAIN → trigger DAG → set DOMAIN → trigger DAG
    trigger_cleanup >> set_domain_account >> trigger_account >> set_domain_facility >> trigger_facility >> set_domain_asset >> trigger_asset >> set_domain_service >> trigger_service
