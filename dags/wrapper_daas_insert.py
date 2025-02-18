import json
from airflow.models import Variable
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

# Define parameters for each domain
domains = {
    "account": {
        "DOMAIN": "account",
        "DOMAIN_SOLR_KEY": "acct_nbr",
        "DOMAIN_SOLR_COLLECTION": "account",
        "UPSERT_PAYLOAD": json.dumps([
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
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
            "INT_ACCT_NBR_01": {
                "acct_code": "INT_US_ACCT_01",
                "acct_name": "Integration account 01"
            },
            "INT_ACCT_NBR_02": {
                "acct_code": "INT_US_ACCT_02",
                "acct_name": "Integration account 02"
            }
        })
    },
    "facility": {
        "DOMAIN": "facility",
        "DOMAIN_SOLR_KEY": "fac_nbr",
        "DOMAIN_SOLR_COLLECTION": "facility",
        "UPSERT_PAYLOAD": json.dumps([
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
        ]),
        "SOLR_EXPECTED_RECORDS": json.dumps({
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
        wait_for_completion=True,  # Wait until the "account" execution completes
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
        wait_for_completion=True,  # Ensures "facility" execution completes
    )

    # Ensure sequential execution: set DOMAIN → trigger DAG → set DOMAIN → trigger DAG
    set_domain_account >> trigger_account >> set_domain_facility >> trigger_facility
