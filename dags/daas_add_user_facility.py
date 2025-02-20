from airflow import DAG # type: ignore
from airflow.providers.postgres.operators.postgres import PostgresOperator # type: ignore
from airflow.utils.dates import days_ago # type: ignore

# Define variables
DAAS_AUTHORIZED_USER = "daas"
INT_FACILITY_JSON = '{"facility_nbr": ["INT_FAC_NBR_01", "INT_FAC_NBR_02"]}'

# Default DAG arguments
default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "catchup": False,
}

# Define DAG
with DAG(
    dag_id="daas_add_user_facility",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # PostgresOperator with parameterized SQL
    add_user_facility_task = PostgresOperator(
        task_id="add_user_facility",
        postgres_conn_id="daas_postgres_us_int",  # Ensure this matches your Airflow connection
        sql="""
            WITH user_data AS (
                SELECT id FROM get_auth_user(%(authorized_user)s) LIMIT 1
            )
            SELECT * FROM add_user_facility(%(facility_json)s, (SELECT id FROM user_data));
        """,
        parameters={
            "authorized_user": DAAS_AUTHORIZED_USER,
            "facility_json": INT_FACILITY_JSON,
        },
        do_xcom_push=False,
    )

    add_user_facility_task
