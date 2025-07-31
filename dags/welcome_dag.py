from airflow import DAG # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','config')))
from default_args import default_args # type: ignore # Arguments par défaut du DAG
import requests

def print_welcome():
    print('Welcome to Airflow!')
    print('Today is {}'.format(datetime.today().date()))

def print_random_quote():
    response = requests.get('https://api.quotable.io/random')
    quote = response.json()['content']
    print('Quote of the day: "{}"'.format(quote))

dag_id = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")
dag = DAG(
    dag_id,
    description="A simple DAG that prints a welcome message and a random quote",
    default_args=default_args,
    schedule_interval='00 9 * * *',
    catchup=False,
)

print_welcome_task = PythonOperator(
    task_id='print_welcome',
    python_callable=print_welcome,
    dag=dag
)

print_random_quote_task = PythonOperator(
    task_id='print_random_quote',
    python_callable=print_random_quote,
    dag=dag
)

# Défini les dépendances entre les tâches
print_welcome_task >> print_random_quote_task