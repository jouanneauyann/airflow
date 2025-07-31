from airflow import DAG # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from airflow.models import Variable # type: ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','config')))
from default_args import default_args # type: ignore # Arguments par défaut du DAG
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','scripts','ogirys')))
import ingestion_ogirys # Module contenant la fonction pour récupérer un token Ogirys # type: ignore
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','scripts','ingestion')))
import ingestion_api # Module contenant les fonctions pour ingérer les données d'une API dans Snowflake # type: ignore
import ingestion_snowflake # Module contenant les fonctions pour ingérer les données dans Snowflake # type: ignore

def execute_get_token():
    body = {
        "username":Variable.get("ogirys_username"),
        "password":Variable.get("ogirys_password"),
        "client_id":Variable.get("ogirys_client_id"),
        "grant_type":Variable.get("ogirys_grant_type")
    }
    url = Variable.get("ogirys_api")
    token = ingestion_ogirys.get_token(url, body)
    return token

def execute_ingestion_api(**kwargs):
    token = kwargs['task_instance'].xcom_pull(task_ids='get_token')
    ingestion_api.ingestion_api(token, 'ogirys')

def execute_ingestion_snowflake(**kwargs):
    ingestion_snowflake.ingestion_snowflake('ogirys') #, conn

dag_id = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")
dag = DAG(
    dag_id,
    description="DAG D'ingestion des données d'Ogyris dans Snowflake",
    default_args=default_args,
    schedule_interval='0 6 * * *',
    catchup=False,
)

get_token_task = PythonOperator(
    task_id='get_token',
    python_callable=execute_get_token,
    dag=dag,
)

extract_api_task = PythonOperator(
    task_id='extract_api',
    python_callable=execute_ingestion_api,
    provide_context=True,
    dag=dag,
)

ingestion_snowflake_task = PythonOperator(
    task_id='ingestion_snowflake',
    python_callable=execute_ingestion_snowflake,
    provide_context=True,
    dag=dag,
)

get_token_task >> extract_api_task >> ingestion_snowflake_task 