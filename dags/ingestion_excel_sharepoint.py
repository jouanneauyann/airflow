from airflow import DAG # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from airflow.models import Variable # type: ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','config')))
from default_args import default_args # type: ignore # Arguments par défaut du DAG
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','scripts','ingestion')))
import ingestion_sharepoint # type: ignore # Script de copie des fichiers depuis SharePoint
import ingestion_excel # type: ignore # Script de conversion des fichiers Excel en CSV
import ingestion_snowflake # type: ignore # Script d'import des CSV dans Snowflake


def execute_copy_from_sharepoint():
    # Variables SharePoint
    site_url = Variable.get("sharepoint_site")
    dossier_sharepoint = Variable.get("sharepoint_folder")
    nom_utilisateur = Variable.get("sharepoint_username")
    mot_de_passe = Variable.get("sharepoint_password")
    # Dossier local pour stocker les fichiers Excel
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dossier_local = os.path.join(current_dir, '..', 'data',f'excel')
    ingestion_sharepoint.copy_from_sharepoint(site_url, dossier_sharepoint, nom_utilisateur, mot_de_passe, dossier_local)

def execute_ingestion_excel(**kwargs):
    ingestion_excel.excel_to_csv('sharepoint')

def execute_ingestion_snowflake(**kwargs):
    ingestion_snowflake.ingestion_snowflake('sharepoint')

dag_id = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")
dag = DAG(
    dag_id,
    description="DAG D'ingestion des fichiers Excel sur SharePoint dans Snowflake",
    default_args=default_args,
    schedule_interval='30 3 * * *',
    tags=['SharePoint'],
    catchup=False,
)

copy_excel_from_sharepoint_task = PythonOperator(
    task_id='copy_excel_from_sharepoint_task',
    python_callable=execute_copy_from_sharepoint,
    dag=dag
)

convert_excel_from_sharepoint_task = PythonOperator(
    task_id='convert_excel_from_sharepoint_task',
    python_callable = execute_ingestion_excel,
    dag=dag
)

ingestion_excel_snowflake_task = PythonOperator(
    task_id='ingestion_excel_snowflake_task',
    python_callable = execute_ingestion_snowflake,
    dag=dag
)



copy_excel_from_sharepoint_task >> convert_excel_from_sharepoint_task >> ingestion_excel_snowflake_task
