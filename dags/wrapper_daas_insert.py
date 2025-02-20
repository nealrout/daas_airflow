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
        "DOMAIN_CACHE_KEY": "account_nbr",
        "DOMAIN_CACHE_COLLECTION": "account",
        "UPSERT_PAYLOAD": json.dumps([
            {
                "account_nbr": "INT_ACCT_NBR_01",
                "account_code": "INT_US_ACCT_01",
                "account_name": "Integration account 01"
            },
            {
                "account_nbr": "INT_ACCT_NBR_02",
                "account_code": "INT_US_ACCT_02",
                "account_name": "Integration account 02"
            }
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_ACCT_NBR_01": {
                "account_code": "INT_US_ACCT_01",
                "account_name": "Integration account 01"
            },
            "INT_ACCT_NBR_02": {
                "account_code": "INT_US_ACCT_02",
                "account_name": "Integration account 02"
            }
        })
    },
    "facility": {
        "DOMAIN": "facility",
        "DOMAIN_CACHE_KEY": "facility_nbr",
        "DOMAIN_CACHE_COLLECTION": "facility",
        "UPSERT_PAYLOAD": json.dumps([
            {
                "account_nbr": "INT_ACCT_NBR_01",
                "facility_code": "INT_US_TEST_01",
                "facility_name": "Integration facility 01",
                "facility_nbr": "INT_FAC_NBR_01"
            },
            {
                "account_nbr": "INT_ACCT_NBR_02",
                "facility_code": "INT_US_TEST_02",
                "facility_name": "Integration facility 02",
                "facility_nbr": "INT_FAC_NBR_02"
            }
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_FAC_NBR_01": {
                "account_nbr": "INT_ACCT_NBR_01",
                "facility_code": "INT_US_TEST_01",
                "facility_name": "Integration facility 01"
            },
            "INT_FAC_NBR_02": {
                "account_nbr": "INT_ACCT_NBR_02",
                "facility_code": "INT_US_TEST_02",
                "facility_name": "Integration facility 02"
            }
        })
    },
    "asset": {
        "DOMAIN": "asset",
        "DOMAIN_CACHE_KEY": "asset_nbr",
        "DOMAIN_CACHE_COLLECTION": "asset",
        "UPSERT_PAYLOAD": json.dumps([
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"sys_id": "INT_system_01",
				"asset_code": "INT_asset_code_01",
				"status_code": "up"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"sys_id": "INT_system_02",
				"asset_code": "INT_asset_code_02",
				"status_code": "down"
			},
			{
				"account_nbr": "INT_ACCT_NBR_02",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"sys_id": "INT_system_03",
				"asset_code": "INT_asset_code_03",
				"status_code": "up"
			},
			{
				"account_nbr": "INT_ACCT_NBR_02",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"sys_id": "INT_system_04",
				"asset_code": "INT_asset_code_04",
				"status_code": "down"
			}
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_ASSET_NBR_01": {
                "account_nbr": "INT_ACCT_NBR_01",
                "facility_nbr": "INT_FAC_NBR_01",
                "sys_id": "INT_system_01",
				"asset_code": "INT_asset_code_01",
				"status_code": "up"
            },
            "INT_ASSET_NBR_02": {
                "account_nbr": "INT_ACCT_NBR_01",
                "facility_nbr": "INT_FAC_NBR_01",
                "sys_id": "INT_system_02",
				"asset_code": "INT_asset_code_02",
				"status_code": "down"
            },
            "INT_ASSET_NBR_03": {
                "account_nbr": "INT_ACCT_NBR_02",
                "facility_nbr": "INT_FAC_NBR_02",
                "sys_id": "INT_system_03",
				"asset_code": "INT_asset_code_03",
				"status_code": "up"
            },
            "INT_ASSET_NBR_04": {
                "account_nbr": "INT_ACCT_NBR_02",
                "facility_nbr": "INT_FAC_NBR_02",
                "sys_id": "INT_system_04",
				"asset_code": "INT_asset_code_04",
				"status_code": "down"
            }
        })
    },
    "service": {
        "DOMAIN": "service",
        "DOMAIN_CACHE_KEY": "service_nbr",
        "DOMAIN_CACHE_COLLECTION": "service",
        "UPSERT_PAYLOAD": json.dumps([
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_nbr": "INT_INT_SVC_NBR_001",
				"service_code": "INT_SVC_CODE_001",
				"service_name": "Integration Service Name 001",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_nbr": "INT_INT_SVC_NBR_002",
				"service_code": "INT_SVC_CODE_002",
				"service_name": "Integration Service Name 002",
				"status_code": "close"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_nbr": "INT_INT_SVC_NBR_003",
				"service_code": "INT_SVC_CODE_003",
				"service_name": "Integration Service Name 003",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_nbr": "INT_INT_SVC_NBR_004",
				"service_code": "INT_SVC_CODE_004",
				"service_name": "Integration Service Name 004",
				"status_code": "close"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_nbr": "INT_INT_SVC_NBR_005",
				"service_code": "INT_SVC_CODE_005",
				"service_name": "Integration Service Name 005",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_nbr": "INT_INT_SVC_NBR_006",
				"service_code": "INT_SVC_CODE_006",
				"service_name": "Integration Service Name 006",
				"status_code": "close"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_nbr": "INT_INT_SVC_NBR_007",
				"service_code": "INT_SVC_CODE_007",
				"service_name": "Integration Service Name 007",
				"status_code": "open"
			},
			{
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_nbr": "INT_INT_SVC_NBR_008",
				"service_code": "INT_SVC_CODE_008",
				"service_name": "Integration Service Name 008",
				"status_code": "close"
			}
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_INT_SVC_NBR_001": {
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_code": "INT_SVC_CODE_001",
				"service_name": "Integration Service Name 001",
				"status_code": "open"
            },
            "INT_INT_SVC_NBR_002": {
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_01",
				"service_code": "INT_SVC_CODE_002",
				"service_name": "Integration Service Name 002",
				"status_code": "close"
            },
            "INT_INT_SVC_NBR_003": {
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_code": "INT_SVC_CODE_003",
				"service_name": "Integration Service Name 003",
				"status_code": "open"
            },
            "INT_INT_SVC_NBR_004": {
				"account_nbr": "INT_ACCT_NBR_01",
				"facility_nbr": "INT_FAC_NBR_01",
				"asset_nbr": "INT_ASSET_NBR_02",
				"service_code": "INT_SVC_CODE_004",
				"service_name": "Integration Service Name 004",
				"status_code": "close"
            },
            "INT_INT_SVC_NBR_005": {
				"account_nbr": "INT_ACCT_NBR_02",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_code": "INT_SVC_CODE_005",
				"service_name": "Integration Service Name 005",
				"status_code": "open"
            },
            "INT_INT_SVC_NBR_006": {
				"account_nbr": "INT_ACCT_NBR_02",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_03",
				"service_code": "INT_SVC_CODE_006",
				"service_name": "Integration Service Name 006",
				"status_code": "close"
            },
            "INT_INT_SVC_NBR_007": {
				"account_nbr": "INT_ACCT_NBR_02",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_code": "INT_SVC_CODE_007",
				"service_name": "Integration Service Name 007",
				"status_code": "open"
            },
            "INT_INT_SVC_NBR_008": {
				"account_nbr": "INT_ACCT_NBR_02",
				"facility_nbr": "INT_FAC_NBR_02",
				"asset_nbr": "INT_ASSET_NBR_04",
				"service_code": "INT_SVC_CODE_008",
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
