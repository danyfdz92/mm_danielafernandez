"""
Airflow DAG for daily ETL workflow - BlueSky Posts.
"""

import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your ETL classes
from data_processes.extract_data import ExtractETL
from data_processes.transform_data import TransformETL
from data_processes.load_data import LoadETL


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=1),
}

dag = DAG(
    dag_id='bluesky_posts_daily_etl_workflow',
    default_args=default_args,
    description='Daily ETL from HuggingFace to SQLite',
    schedule_interval=datetime.timedelta(days=1),  # Once a day
    start_date=datetime.datetime(2024, 1, 1),      # Arbitrary start date
    catchup=False
)

def extract_callable(**kwargs):
    """
    Extract step: Pass the dataset URL to the constructor.
    """
    dataset_url = "alpindale/two-million-bluesky-posts"
    extractor = ExtractETL(dataset_url=dataset_url)
    data = extractor.run_extract()
    kwargs['ti'].xcom_push(key='raw_data', value=data)

def transform_callable(**kwargs):
    """
    Transform step: Pass the list of columns to check for blanks.
    """
    raw_data = kwargs['ti'].xcom_pull(key='raw_data')
    transformer = TransformETL(columns_to_check=["uri", "created_at"])
    transformed_data = transformer.run_transform(raw_data)
    kwargs['ti'].xcom_push(key='transformed_data', value=transformed_data)

def load_callable(**kwargs):
    """
    Load step: Load the transformed data into SQLite.
    """
    # Compute absolute path to the JSON file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query_path = os.path.join(project_root, "database_admin", "query_files", "bluesky_daily.json")

    transformed_data = kwargs['ti'].xcom_pull(key='transformed_data')
    loader = LoadETL(database_path='bluesky_posts.db', query_path=query_path)
    loader.run_load(transformed_data)

extract_task = PythonOperator(
    task_id='extract_task',
    python_callable=extract_callable,
    provide_context=True,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_task',
    python_callable=transform_callable,
    provide_context=True,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_task',
    python_callable=load_callable,
    provide_context=True,
    dag=dag
)

extract_task >> transform_task >> load_task