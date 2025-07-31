import os

# Fonction qui sera exécutée en cas d'échec
def create_error_log(context):

    dag_id = context.get('dag').dag_id
    task_id = context.get('task_instance').task_id
    execution_date = context.get('execution_date').strftime("%Y-%m-%d %H:%M:%S")
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 
    file_name = os.path.join(current_dir, '..', 'zabbix',f'{dag_id}.txt')
    
    # Contenu du fichier
    content = f"Date de l'erreur : {execution_date}\n Task en échec : {task_id}\n"

    # Écriture du fichier
    with open(file_name, "a") as file:  # "a" pour ajouter du texte si le fichier existe déjà
        file.write(content)
    
    print(f"✅ Fichier créé : {file_name}")