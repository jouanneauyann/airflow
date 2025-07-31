from airflow import DAG # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from airflow.models import Variable # type: ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','config')))
from default_args import default_args # type: ignore # Arguments par défaut du DAG
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','scripts','glpi')))
import ingestion_glpi # Module contenant la fonction pour récupérer un token Ogirys # type: ignore




def execute_get_connexion_glpi():
    body = {
        "host": Variable.get("glpi_host"),
        "user": Variable.get("glpi_user"),
        "password": Variable.get("glpi_password"),
        "database": Variable.get("glpi_database"),
        "port": int(Variable.get("glpi_port"))
}

    conn = ingestion_glpi.get_connexion_glpi(body)
    print("Connexion réussie")



dag_id = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")

dag = DAG(
    dag_id,
    default_args=default_args,
    schedule_interval='0 5 * * *',
    catchup=False,
)

get_connexion_glpi_task = PythonOperator(
    task_id='get_cegid_connexion',
    python_callable=execute_get_connexion_glpi,
    dag=dag,
)



get_connexion_glpi_task