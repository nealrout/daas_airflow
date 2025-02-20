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
        "DOMAIN_KEY": "account_nbr",
        "DOMAIN_CACHE_COLLECTION": "account",
        "API_POST_DB_SEARCH": json.dumps({
			"account_nbr": ["INT_ACCT_NBR_01", "INT_ACCT_NBR_02"]
			,"account_code":["INT_US_ACCT_01", "INT_US_ACCT_02"]
			,"account_name":["Integration account 01", "Integration account 01"]
        }),
        "API_POST_DB_SEARCH_RESULTS": json.dumps({
            "INT_ACCT_NBR_01": {
                "account_code": "INT_US_ACCT_01",
                "account_name": "Integration account 01"
            },
            "INT_ACCT_NBR_02": {
                "account_code": "INT_US_ACCT_02",
                "account_name": "Integration account 02"
            }
        }),
        "API_POST_CACHE_SEARCH": json.dumps({
            "fq": [
                "account_nbr:(INT_ACCT_NBR_01 INT_ACCT_NBR_02)",
                "account_code:(INT_US_ACCT_01 INT_US_ACCT_02)",
                "account_name:(\"Integration account 01\" \"Integration account 02\")"
            ],
            "q": "*:*",
            "rows": 100
        }),
        "API_POST_CACHE_SEARCH_RESULTS": json.dumps({
            "INT_ACCT_NBR_01": {
                "account_code": "INT_US_ACCT_01",
                "account_name": "Integration account 01"
            },
            "INT_ACCT_NBR_02": {
                "account_code": "INT_US_ACCT_02",
                "account_name": "Integration account 02"
            }
        }),
    },
    "facility": {
        "DOMAIN": "facility",
        "DOMAIN_KEY": "facility_nbr",
        "DOMAIN_CACHE_COLLECTION": "facility",
        "API_POST_DB_SEARCH": json.dumps({
            "account_nbr": ["INT_ACCT_NBR_01", "INT_ACCT_NBR_02"]
            ,"facility_nbr": ["INT_FAC_NBR_01", "INT_FAC_NBR_02"]
            ,"facility_code":["INT_US_TEST_01", "INT_US_TEST_02"]
            ,"facility_name":["Integration facility 01", "Integration facility 02"]
        }),
        "API_POST_DB_SEARCH_RESULTS": json.dumps({
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
        }),
        "API_POST_CACHE_SEARCH": json.dumps({
            "fq": [
            "account_nbr:(INT_ACCT_NBR_01 INT_ACCT_NBR_02)",
            "facility_nbr:(INT_FAC_NBR_01 INT_FAC_NBR_02)",
            "facility_code:(INT_US_TEST_01 INT_US_TEST_02)",
            "facility_name:(\"Integration facility 01\" \"Integration facility 02\")"
            ],
            "q": "*:*",
            "rows": 100
        }),
        "API_POST_CACHE_SEARCH_RESULTS": json.dumps({
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
        }),
    },
    "asset": {
        "DOMAIN": "asset",
        "DOMAIN_KEY": "asset_nbr",
        "DOMAIN_CACHE_COLLECTION": "asset",
        "API_POST_DB_SEARCH": json.dumps({
            "account_nbr": ["INT_ACCT_NBR_01","INT_ACCT_NBR_02"]
            ,"facility_nbr": ["INT_FAC_NBR_01", "INT_FAC_NBR_02"]
            ,"asset_nbr": ["INT_ASSET_NBR_01", "INT_ASSET_NBR_02","INT_ASSET_NBR_03","INT_ASSET_NBR_04"]
            ,"sys_id": ["INT_system_01","INT_system_02","INT_system_03","INT_system_04"]
            ,"status_code": ["up","down"]
        }),
        "API_POST_DB_SEARCH_RESULTS": json.dumps({
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
        }),
        "API_POST_CACHE_SEARCH": json.dumps({
        "fq": [
            "account_nbr:(INT_ACCT_NBR_01 INT_ACCT_NBR_02)",
            "asset_nbr:(INT_ASSET_NBR_01 INT_ASSET_NBR_02 INT_ASSET_NBR_03 INT_ASSET_NBR_04)",
            "sys_id:(INT_system_01 INT_system_02 INT_system_03 INT_system_04)",
            "facility_nbr:(INT_FAC_NBR_01 INT_FAC_NBR_02)"
        ],
        "q": "*:*",
        "rows": 100
        }),
        "API_POST_CACHE_SEARCH_RESULTS": json.dumps({
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
        }),
    },
    "service": {
        "DOMAIN": "service",
        "DOMAIN_KEY": "service_nbr",
        "DOMAIN_CACHE_COLLECTION": "service",
        "API_POST_DB_SEARCH": json.dumps({
            "account_nbr": ["INT_ACCT_NBR_01","INT_ACCT_NBR_02"]
            ,"facility_nbr": ["INT_FAC_NBR_01","INT_FAC_NBR_02"]
            ,"asset_nbr": ["INT_ASSET_NBR_01","INT_ASSET_NBR_02","INT_ASSET_NBR_03","INT_ASSET_NBR_04"]
            ,"service_nbr" :["INT_INT_SVC_NBR_001","INT_INT_SVC_NBR_002","INT_INT_SVC_NBR_003","INT_INT_SVC_NBR_004","INT_INT_SVC_NBR_005","INT_INT_SVC_NBR_006","INT_INT_SVC_NBR_007","INT_INT_SVC_NBR_008"]
            ,"status_code": ["open","close"]
        }),
        "API_POST_DB_SEARCH_RESULTS": json.dumps({
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
        }),
        "API_POST_CACHE_SEARCH": json.dumps({
            "fq": [
                "account_nbr:(INT_ACCT_NBR_01 INT_ACCT_NBR_02)"
                ,"facility_nbr:(INT_FAC_NBR_01 INT_FAC_NBR_02)"
                ,"asset_nbr:(INT_ASSET_NBR_01 INT_ASSET_NBR_02 INT_ASSET_NBR_03 INT_ASSET_NBR_04)"
                ,"service_nbr:(INT_INT_SVC_NBR_001 INT_INT_SVC_NBR_002 INT_INT_SVC_NBR_003 INT_INT_SVC_NBR_004 INT_INT_SVC_NBR_005 INT_INT_SVC_NBR_006 INT_INT_SVC_NBR_007 INT_INT_SVC_NBR_008)"
            ],
            "q": "*:*",
            "rows": 100
        }),
        "API_POST_CACHE_SEARCH_RESULTS": json.dumps({
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
        }),
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
    set_domain_account >> trigger_account >> set_domain_facility >> trigger_facility >> set_domain_asset >> trigger_asset >> set_domain_service >> trigger_service
    # set_domain_account >> trigger_account 
