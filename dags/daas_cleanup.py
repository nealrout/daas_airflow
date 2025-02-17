from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago
import json
import base64

SOLR_COLLECTION_ACCOUNT = "account"
SOLR_COLLECTION_FACILITY = "facility"
SOLR_COLLECTION_ASSET = "asset"
SOLR_COLLECTION_SERVICE = "service"

with DAG(
    dag_id="daas_cleanup",
    schedule_interval=None,  # Manual trigger
    start_date=days_ago(1),
    catchup=False,
) as dag:
    # Cleanup DB data
    clean_integration_data = PostgresOperator(
        task_id="clean_integration_data",
        postgres_conn_id="postgres_us_int_daas",  
        sql="CALL clean_integration_data();",  
    )
    # Cleanup SOLR ACCOUNT data
    clean_solr_account = SimpleHttpOperator(
        task_id="clean_solr_account",
        http_conn_id="solr_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_ACCOUNT}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "acct_nbr:INT_*"}}),
        # data=json.dumps({"delete": {"id": "INT_ACCT_NBR_01"}}),  
        log_response=True,  # 
    )
    # Cleanup SOLR ACCOUNT data
    clean_solr_facility= SimpleHttpOperator(
        task_id="clean_solr_facility",
        http_conn_id="solr_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_FACILITY}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "fac_nbr:INT_*"}}),
        # data=json.dumps({"delete": {"id": "INT_ACCT_NBR_01"}}),  
        log_response=True,  # 
    )
    # Cleanup SOLR ASSET data
    clean_solr_asset = SimpleHttpOperator(
        task_id="clean_solr_asset",
        http_conn_id="solr_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_ASSET}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "asset_nbr:INT_*"}}),
        # data=json.dumps({"delete": {"id": "INT_ACCT_NBR_01"}}),  
        log_response=True,  # 
    )
    # Cleanup SOLR SERVICE data
    clean_solr_service = SimpleHttpOperator(
        task_id="clean_solr_service",
        http_conn_id="solr_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_SERVICE}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "svc_nbr:INT_*"}}),
        # data=json.dumps({"delete": {"id": "INT_ACCT_NBR_01"}}),  
        log_response=True,  # 
    )

    clean_solr_account >> clean_solr_facility>> clean_solr_asset >> clean_solr_service >> clean_integration_data