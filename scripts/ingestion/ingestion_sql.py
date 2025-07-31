"""
Comment va fonctionner l'ingestion de requêtes SQL dans Snowflake ?
# 1. Création d'une connexion à la BDD source (par exemple, CEGID, GLPI, etc.)
# 2. Exécution de la requête SQL pour récupérer les données

"""
import os
import sys
import itertools
import pymssql # type: ignore
import pandas as pd # type: ignore
import jinja2   # type: ignore pour gérer le template SQL
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import module_global # type: ignore


def ingestion_sql(source_name, password):
    # 0. Import du fichier de configuration
    config_yaml = module_global.get_config_yaml(source_name)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 1. Réinitialisation du dossier data
    module_global.reinitialisation_dossier_data(config_yaml)

    # 2. Récupération de la connexion à la BDD => Possiblement créé une fonction get_connexion
    if config_yaml['type_source']=='mssql':
        print("🔄️ Récupération de la connexion à la BDD MSSQL")
        conn = pymssql.connect(server=config_yaml['server'],
                        user=config_yaml['username'],
                        password=password,
                        database=config_yaml['database'])

    # 3. Exécution des requêtes SQL 
    for method in config_yaml["list_method"]:
        nom_requete = list(method.keys())[0]
        requete_sql_file = os.path.join(current_dir, '..', source_name, method['sql'])
        # Lire la requête SQL depuis le fichier
        with open(requete_sql_file, "r") as f:
            requete_template = jinja2.Template(f.read())

        filtres = method["filtres"] if "filtres" in method else {}
        print(filtres)

        # on produit la cartésienne de tous les filtres
        filtres_combinations = []
        if filtres:
            keys, values = zip(*filtres.items())
            for combination in itertools.product(*values):
                filtres_combinations.append(dict(zip(keys, combination)))
        else:
            filtres_combinations.append({})

        for filtres_combinaison in filtres_combinations:
            rendered_query = requete_template.render(filtres=filtres_combinaison)
            print(f"🔄️ Exécution de la requête {nom_requete} avec filtres {filtres_combinaison}")
            print("---- requête exécutée ----")
            print(rendered_query)
            print("--------------------------")
            df = pd.read_sql_query(rendered_query, conn)

            # suffix clair ex: comptes_2023_V
            suffix = "_".join(str(v) for v in filtres_combinaison.values())
            parquet_filename = f"{nom_requete}_{suffix}.parquet"
            file_name = os.path.join(current_dir, '..', '..', 'data', source_name, nom_requete, parquet_filename)
            df.to_parquet(file_name, index=False)
            print(f"✅ Sauvegarde dans {file_name}")
