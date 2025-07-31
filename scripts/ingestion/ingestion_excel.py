import os
import shutil
import sys
import pandas as pd # type: ignore
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import module_global # type: ignore

def excel_to_csv(source_name):
    config_yaml = module_global.get_config_yaml(source_name)
    module_global.reinitialisation_dossier_data(config_yaml)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for method in config_yaml["list_method"]:
        nom_requete = list(method.keys())[0]
        # Conversion des fichiers Excel
        for file in method[nom_requete]:
            file_path = os.path.join(current_dir,'..','..','data','excel', file)
            df = pd.read_excel(file_path, sheet_name=nom_requete)
            df.columns = [col.replace(' ', '_').replace('é', 'e') for col in df.columns]
            df.to_csv(os.path.join(current_dir, '..', '..', 'data', source_name, f"{nom_requete}", f"{nom_requete.replace(' ','')}_{file.replace('.xlsx', '')}.csv"), index=False)
            print(f"Fichier {file} converti en CSV et enregistré dans {os.path.join(current_dir, '..', '..', 'data', source_name, f'{nom_requete}')}")

