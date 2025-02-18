import json
from airflow.models import Variable
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago


account_params = {
    "DOMAIN": "facility",
    "DOMAIN_SOLR_KEY": "fac_nbr",
    "DOMAIN_SOLR_COLLECTION": "facility",
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
}
facility_params = {
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

# Store in Airflow Variables
for key, value in facility_params.items():
    Variable.set(key, value)

with DAG(
    dag_id="wrapper_daas_insert",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    trigger_child_dag = TriggerDagRunOperator(
        task_id="trigger_child_dag",
        trigger_dag_id="daas_insert_generic",
        conf={},  # Not passing directly, using Variables
    )
    
    trigger_child_dag
