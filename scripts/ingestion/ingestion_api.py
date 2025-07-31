# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import requests
import json
import os
import shutil
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import module_global # type: ignore


def ingestion_api(Authorization_token, source_name):
    """
    Fonction permettant de récupérer les données json d'une API et de les stocker dans le répertoire ../../data/{nom_source}/{nom_requete}
    """
    
    config_yaml = module_global.get_config_yaml(source_name)
    module_global.reinitialisation_dossier_data(config_yaml)
    
    for method in config_yaml["list_method"]:
        if method["loop_url"]=='oui':
            loop_api(Authorization_token, source_name, config_yaml, method)
        else:
            call_api("", "",Authorization_token, source_name, config_yaml, method)

def loop_api(Authorization_token, source_name,config_yaml, method):
    """
    Cette boucle permet de boucler sur les variables présentes dans loop_url
    """
    loop_url = config_yaml["loop_url"]
    for item in loop_url:
        nom_variable = item["nom_variable"]
        list_value = item["valeurs"]
        for value in list_value:
            call_api(value, nom_variable,Authorization_token, source_name, config_yaml, method)

def call_api(p_value, p_value_name, Authorization_token, source_name, config_yaml, method):
    """
    Génère l'URL de la requête API et appel une fonction pour traiter la requête
    """
    url = config_yaml["url"]
    authorization = config_yaml["authorization"]

    url_method = construct_url(url, method, Authorization_token, authorization, config_yaml, p_value, p_value_name)
    nom_requete = list(method.keys())[0]

    if "loop_method" in method:
        handle_loop_method(method, url_method, source_name, nom_requete, p_value, config_yaml)
    else:
        save_response(url_method, source_name, nom_requete, p_value)


def construct_url(base_url, method, Authorization_token, authorization, config_yaml, p_value, p_value_name):
    """
    Construit l'URL complète avec les paramètres et remplacements nécessaires.
    """
    url_parameters = []
    for parameter in method["parameters"]:
        for key, value in parameter.items():
            url_parameters.append(f"{key}={value}")

    if authorization["type"] == 'parameter':
        url_parameters.append(f"{authorization['name']}={Authorization_token}")

    url_method = f"{base_url}{method['module']}?{'&'.join(url_parameters)}"
    url_method = url_method.replace("__var_date_debut_mois__", module_global.debutMois("%Y-%m-%d", config_yaml))
    url_method = url_method.replace("__var_date_fin_mois__", module_global.finMois("%Y-%m-%d", config_yaml))
    url_method = url_method.replace(f"__var_{p_value_name}__", str(p_value))

    return url_method


def handle_loop_method(method, url_method, source_name, nom_requete, p_value, config_yaml):
    """
    Gère les boucles spécifiques définies dans `loop_method`.
    """
    loop_method = method["loop_method"]
    if loop_method['type_boucle'] == "quotidien":
        dates = loop_daily(loop_method, config_yaml)
        for date in dates:
            url_method_loop = url_method.replace(loop_method['nom_variable_debut'], date[0])
            url_method_loop = url_method_loop.replace(loop_method['nom_variable_fin'], date[1])
            save_response(url_method_loop, source_name, nom_requete, p_value, date)


def save_response(url, source_name, nom_requete, p_value, date_range=None):
    """
    Effectue la requête HTTP et sauvegarde la réponse dans un fichier JSON.
    """
    response = requests.get(url)
    response_data = json.loads(response.text)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if date_range:
        file_name = f"{nom_requete}_{p_value}_{date_range[0]}_{date_range[1]}.json"
    elif p_value != "":
        file_name = f"{nom_requete}_{p_value}.json"
    else:
        file_name = f"{nom_requete}.json"

    data_dir = os.path.join(current_dir, '..', '..', 'data', source_name, nom_requete, file_name)
    with open(data_dir, "w") as file:
        json.dump(response_data, file, indent=4)
    print(f"Le fichier {file_name} a bien été créé.")

def loop_daily(loop_method,config_yaml):
    """
    Fonction permettant de générer les plages de dates à intérroger
    dates: liste de liste de dates de début et de fin allant du premier au dernier jour du mois
    """
    interval = loop_method['interval']
    date_debut_requete = loop_method['date_debut_requete']  
    date_fin_requete = loop_method['date_fin_requete']
    if date_debut_requete == "__var_date_debut_mois__":
        date_debut_requete = datetime.strptime(module_global.debutMois("%Y-%m-%d",config_yaml ), '%Y-%m-%d')
    if date_fin_requete == "__var_date_fin_mois__":
        date_fin_requete = datetime.strptime(module_global.finMois("%Y-%m-%d", config_yaml), '%Y-%m-%d')
    
    date_debut = date_debut_requete
    date_fin = date_fin_requete
    dates = []
    while date_debut < date_fin_requete:
        date_fin = date_debut + timedelta(days=interval)
        if date_fin > date_fin_requete:
            date_fin = date_fin_requete
        dates.append([date_debut.strftime('%Y-%m-%d'), date_fin.strftime('%Y-%m-%d')])
        date_debut += timedelta(days=interval+1)
    return dates
