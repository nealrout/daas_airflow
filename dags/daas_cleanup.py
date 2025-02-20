from airflow import DAG # type: ignore
from airflow.providers.http.operators.http import SimpleHttpOperator # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from airflow.providers.postgres.operators.postgres import PostgresOperator # type: ignore
from airflow.utils.dates import days_ago # type: ignore
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
        postgres_conn_id="daas_postgres_us_int",  
        sql="CALL clean_integration_data();",  
    )
    # Cleanup SOLR ACCOUNT data
    clean_solr_account = SimpleHttpOperator(
        task_id="clean_solr_account",
        http_conn_id="daas_cache_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_ACCOUNT}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "account_nbr:INT_*"}}),
        log_response=True,  # 
    )
    # Cleanup SOLR ACCOUNT data
    clean_solr_facility= SimpleHttpOperator(
        task_id="clean_solr_facility",
        http_conn_id="daas_cache_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_FACILITY}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "facility_nbr:INT_*"}}),
        log_response=True,  # 
    )
    # Cleanup SOLR ASSET data
    clean_solr_asset = SimpleHttpOperator(
        task_id="clean_solr_asset",
        http_conn_id="daas_cache_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_ASSET}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "asset_nbr:INT_*"}}),
        log_response=True,  # 
    )
    # Cleanup SOLR SERVICE data
    clean_solr_service = SimpleHttpOperator(
        task_id="clean_solr_service",
        http_conn_id="daas_cache_integration", 
        endpoint=f"/solr/{SOLR_COLLECTION_SERVICE}/update?commit=true",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({"delete": {"query": "service_nbr:INT_*"}}),
        log_response=True,  # 
    )

    clean_solr_account >> clean_solr_facility>> clean_solr_asset >> clean_solr_service >> clean_integration_data