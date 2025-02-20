from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow import DAG
from airflow.utils.dates import days_ago

with DAG(
    dag_id="master_daas_dag",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    def log_child_dag_execution_func(context):
        triggered_run_id = context["task_instance"].xcom_pull(task_ids="trigger_child_dag")
        print(f"🔗 Click here to open Child DAG: http://your-airflow-url/dags/child_dag/grid?execution_date={triggered_run_id}")


    trigger_wrapper_daas_insert = TriggerDagRunOperator(
        task_id="trigger_wrapper_daas_insert",
        trigger_dag_id="wrapper_daas_insert",
        wait_for_completion=True,
        on_success_callback=log_child_dag_execution_func
    )

    trigger_wrapper_daas_search = TriggerDagRunOperator(
        task_id="trigger_wrapper_daas_search",
        trigger_dag_id="wrapper_daas_search",
        wait_for_completion=True,
        on_success_callback=log_child_dag_execution_func
    )

    trigger_wrapper_daas_insert >> trigger_wrapper_daas_search 
