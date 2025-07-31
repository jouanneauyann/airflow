import os
import yaml # type: ignore
from datetime import datetime, timedelta
import calendar
import shutil

def get_config_yaml(source_name):
    """
    Charge le fichier de configuration YAML pour la source spécifiée.
    
    :param source_name: Nom de la source pour laquelle charger la configuration.
    :return: Dictionnaire contenant la configuration de la source.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_config_file = os.path.join(current_dir, '..', source_name,f'config_{source_name}.yaml')
    with open(yaml_config_file) as config_file:
        config_yaml = yaml.load(config_file.read(), Loader=yaml.FullLoader)
    return config_yaml


def reinitialisation_dossier_data(config_yaml):
    """
    Réinitialise le dossier data pour chaque requête définie dans le fichier de configuration YAML.
    
    :param config_yaml: Dictionnaire contenant la configuration de la source.
    :return: None
    """
    source_name = config_yaml["source_name"]
    for method in config_yaml["list_method"]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        nom_requete = list(method.keys())[0]
        if os.path.exists(os.path.join(current_dir, '..', '..','data',source_name,f"{nom_requete}")):
            shutil.rmtree(os.path.join(current_dir, '..', '..','data',source_name,f"{nom_requete}"))
        os.makedirs(os.path.join(current_dir, '..', '..','data',source_name,f"{nom_requete}"))
        print(f"Répertoire de la requête {nom_requete} réinitialisé dans le dossier data/{source_name}/{nom_requete}")

def debutMois(format_str, config_yaml):    
    """
    Retourne le premier jour du mois courant selon le format spécifié.

    :param format_str: Chaîne de format pour la date (ex: "%Y-%m-%d", "%d/%m/%Y", etc.).
    :param config_yaml: Dictionnaire de configuration contenant les variables globales.
    :return: Date formatée en chaîne de caractères.
    """
    var_date_debut_mois = 0 
    if "variable_globale" in config_yaml:
        variable_globale = config_yaml["variable_globale"]
        if "var_date_debut_mois" in variable_globale:
            var_date_debut_mois = variable_globale["var_date_debut_mois"]
    now = datetime.now() + timedelta(days=var_date_debut_mois)
    first_day = datetime(now.year, now.month, 1)
    return format_date(first_day, format_str)

def finMois(format_str, config_yaml):
    """
    Retourne le dernier jour du mois courant selon le format spécifié.

    :param format_str: Chaîne de format pour la date (ex: "%Y-%m-%d", "%d/%m/%Y", etc.).
    :param config_yaml: Dictionnaire de configuration contenant les variables globales.
    :return: Date formatée en chaîne de caractères.
    """
    var_date_fin_mois = 0 
    if "variable_globale" in config_yaml:
        variable_globale = config_yaml["variable_globale"]
        if "var_date_fin_mois" in variable_globale:
            var_date_fin_mois = variable_globale["var_date_fin_mois"]
    now = datetime.now() + timedelta(days=var_date_fin_mois)
    last_day = datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    return format_date(last_day, format_str)

def format_date(date: datetime, format_str: str) -> str:
    """
    Formatte une date donnée selon le format spécifié.

    :param date: Objet datetime à formater.
    :param format_str: Chaîne de format (ex: "%Y-%m-%d", "%d/%m/%Y", etc.).
    :return: Date formatée en chaîne de caractères.
    """
    return date.strftime(format_str)