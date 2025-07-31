"""
DAG d'ingestion des données de CEGID dans Snowflake.
Il exécute : 
- ingestion_cegid.get_connexion_cegid : Récupération de la connexion à CEGID
"""

from airflow import DAG # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from airflow.models import Variable # type: ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','config')))
from default_args import default_args # type: ignore # Arguments par défaut du DAG
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','scripts','ingestion')))
import ingestion_sql # Module contenant la fonction pour récupérer un token Ogirys # type: ignore
import ingestion_snowflake # Module contenant la fonction pour ingérer les données dans Snowflake # type: ignore

def execute_ingestion_cegid():
    password = Variable.get("cegid_password")
    ingestion_sql.ingestion_sql("cegid", password)

def execute_cegid_snowflake():
    ingestion_snowflake.ingestion_snowflake("cegid")

dag_id = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")
dag = DAG(
    dag_id,
    description="DAG D'ingestion des données de CEGID dans Snowflake",
    default_args=default_args,
    schedule_interval='0 5 * * *',
    catchup=False,
)

execute_ingestion_cegid_task = PythonOperator(
    task_id='execute_ingestion_cegid',
    python_callable=execute_ingestion_cegid,
    dag=dag,
)

execute_cegid_snowflake_task = PythonOperator(
    task_id='execute_cegid_snowflake',
    python_callable=execute_cegid_snowflake,
    dag=dag,
)

execute_ingestion_cegid_task >> execute_cegid_snowflake_task