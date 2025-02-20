from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago

# Define DAG
with DAG(
    dag_id="test_local_postgres_connection",
    schedule_interval=None,  # Manual trigger
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Query the local PostgreSQL database from Airflow (inside Docker)
    test_postgres = PostgresOperator(
        task_id="test_local_postgres",
        postgres_conn_id="daas_postgres_us_int",  # ✅ Uses the Airflow Connection we set up
        sql="SELECT NOW();",  # Simple query to test connection
    )

    test_postgres
