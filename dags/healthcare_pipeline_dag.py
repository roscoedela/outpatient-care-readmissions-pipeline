from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_ROOT = "/usr/local/airflow"

default_args = {
    "owner": "rooscol",
    "depends_on_past": False,
    "retries": 0,
}


with DAG(
    dag_id="healthcare_pipeline_dag",
    description="End-to-end healthcare analytics capstone pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["healthcare", "dbt", "snowflake", "capstone"],
) as dag:

    extract_physicians_api = BashOperator(
        task_id="extract_physicians_api",
        bash_command=f"""
        cd {PROJECT_ROOT} &&
        python ingestion/fetch_physicians_api.py
        """,
    )

    validate_sources = BashOperator(
        task_id="validate_sources",
        bash_command=f"""
        cd {PROJECT_ROOT} &&
        python ingestion/validate_sources.py
        """,
    )

    load_raw_to_snowflake = BashOperator(
        task_id="load_raw_to_snowflake",
        bash_command=f"""
        cd {PROJECT_ROOT} &&
        python ingestion/load_raw_to_snowflake.py
        """,
    )

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"""
        cd {PROJECT_ROOT}/healthcare_dbt &&
        dbt run --select staging
        """,
    )

    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=f"""
        cd {PROJECT_ROOT}/healthcare_dbt &&
        dbt run --select mart_state_healthcare_summary mart_hospital_quality
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"""
        cd {PROJECT_ROOT}/healthcare_dbt &&
        dbt test
        """,
    )

    extract_physicians_api >> validate_sources >> load_raw_to_snowflake >> dbt_run_staging >> dbt_run_marts >> dbt_test