from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Define the default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
}

# Create the DAG object
with DAG(
    dag_id="bluesky_posts_daily",
    default_args=default_args,
    description="A simple test DAG for Airflow",
    schedule_interval=None,  # Manually trigger only
    catchup=False,
) as dag:

    # Define the Python task
    def say_hello():
        print("Hello, Airflow!")

    hello_task = PythonOperator(
        task_id="say_hello_task",
        python_callable=say_hello,
    )

    # Set task dependencies
    hello_task
