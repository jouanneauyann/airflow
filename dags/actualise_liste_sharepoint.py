from airflow import DAG # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from airflow.models import Variable # type: ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','config')))
from default_args import default_args # type: ignore # Arguments par défaut du DAG
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','scripts','ingestion')))
import ingestion_sharepoint # type: ignore 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','scripts','interop')))
import actualisation_liste_sharepoint # type: ignore 


def execute_actualisation_liste_sharepoint():
    site_url = Variable.get("sharepoint_site_rh")
    username = Variable.get("sharepoint_username")
    password = Variable.get("sharepoint_password")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(current_dir,'..','data','excel', 'SourcesListesSharePoint.xlsx')
    mapping = {
        "ESAT":"ESAT",
        "INTERIM":"SalariesFacilit",
        "NDF":"Salaries"
    }
    # Authentification
    ctx = ingestion_sharepoint.get_sharepoint_context(site_url, username, password)

    actualisation_liste_sharepoint.actualise_liste_sharepoint(ctx, excel_path, mapping)

dag_id = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")
dag = DAG(
    dag_id,
    description="DAG transverse permettant d'actualiser des listes SharePoint à partir d'un fichier Excel",
    default_args=default_args,
    schedule_interval='30 3 * * *',
    tags=['sharepoint_grh'],
    catchup=False,
)

actualisation_liste_sharepoint_task = PythonOperator(
    task_id='actualisation_liste_sharepoint_task',
    python_callable=execute_actualisation_liste_sharepoint,
    dag=dag
)


actualisation_liste_sharepoint_task
