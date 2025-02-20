Copy-Item -Path "D:\src\github\daas_airflow\dags\*.py" -Destination "D:\home\airflow-docker\dags\"

docker exec -it airflow-docker-airflow-scheduler-1 airflow dags reserialize
