from office365.sharepoint.client_context import ClientContext # type: ignore
from office365.runtime.auth.authentication_context import AuthenticationContext # type: ignore
import os
import shutil
import pandas as pd # type: ignore
import time

def copy_from_sharepoint(site_url, dossier_sharepoint, nom_utilisateur, mot_de_passe, dossier_local):
    """
    Description:
        Télécharge tous les fichiers Excel (.xlsx, .xls, .xlsm) depuis un dossier SharePoint vers un dossier local.
    
    Args:
        site_url (str): URL du site SharePoint ("https://sico.sharepoint.com/sites/nomdusite").
        dossier_sharepoint (str): Chemin relatif du dossier SharePoint (ex: "/sites/nomdusite/Documents partagés/fichiers"). 
            - Séparez les dossier_sharepoint par `__split__` si vous souhaitez télécharger des fichiers excel depuis plusieurs dossiers SharePoint.
        nom_utilisateur (str): Nom d'utilisateur SharePoint (ex: "prenom.nom@fondation-ove.com").
        mot_de_passe (str): Mot de passe associé à l'utilisateur.
        dossier_local (str): Chemin local où enregistrer les fichiers Excel téléchargés.

    Returns:
        None

    Print:
        - Le nom de chaque fichier téléchargé
        - Un message erreur si authentification échoue

    Remarques:
        - Seuls les fichiers ayant une extension `.xlsx`, `.xls` ou `.xlsm` sont téléchargés.
        - Le dossier local doit exister avant l'exécution de la fonction.
    """
    # Vider le dossier local avant téléchargement
    for fichier in os.listdir(dossier_local):
        chemin_fichier = os.path.join(dossier_local, fichier)
        if os.path.isfile(chemin_fichier):
            os.remove(chemin_fichier)
        elif os.path.isdir(chemin_fichier):
            shutil.rmtree(chemin_fichier)
    
    # Créer le contexte SharePoint
    ctx = get_sharepoint_context(site_url, nom_utilisateur, mot_de_passe)

    for repository in dossier_sharepoint.split('__split__'):
        dossier = ctx.web.get_folder_by_server_relative_url(repository)
        fichiers = dossier.files
        ctx.load(fichiers)
        ctx.execute_query()

        for f in fichiers:
            nom_fichier = f.properties["Name"]
            if nom_fichier.endswith(('.xlsx', '.xls', '.xlsm')):
                print(f"Téléchargement : {nom_fichier}")
                chemin_local = os.path.join(dossier_local, nom_fichier)

                # Ouvrir le fichier local en écriture binaire et télécharger dedans
                with open(chemin_local, "wb") as output_file:
                    f.download(output_file)
                    ctx.execute_query()


def get_sharepoint_context(site_url, nom_utilisateur, mot_de_passe):
    """
    Créé un contexte SharePoint pour interagir avec le site.
    :param site_url: URL du site SharePoint
    :param nom_utilisateur: Nom d'utilisateur pour l'authentification
    :param mot_de_passe: Mot de passe pour l'authentification
    :return: ClientContext pour interagir avec SharePoint
    """
    ctx_auth = AuthenticationContext(site_url)
    ctx_auth.acquire_token_for_user(nom_utilisateur, mot_de_passe)
    ctx = ClientContext(site_url, ctx_auth)
    return ctx




def actualise_liste_sharepoint(ctx, excel_path, mapping):
    # Charger les données Excel
    excel_data = pd.read_excel(excel_path, sheet_name=None)  # toutes les feuilles

    for sheet_name, list_name in mapping.items():

        target_list = ctx.web.lists.get_by_title(list_name)
        fields = target_list.fields.get().execute_query()
        vide_liste_sharepoint(ctx, target_list)

        df = excel_data[sheet_name].dropna(how='all') 
        print(f"\n🔄 Import de '{sheet_name}' vers la liste SharePoint '{list_name}' ({len(df)} lignes)")
        
        for _, row in df.iterrows():
            item_data = {}
            for field in fields:
                if field.title in df.columns:
                    value = row[field.title]
                    sharepoint_field = field.internal_name
                    # Évite d'envoyer des NaN (qui plantent)
                    if pd.isna(value):
                        continue

                    # Cast forcé pour les strings
                    if isinstance(value, (int, float)):
                        value = str(value)
                    elif isinstance(value, pd.Timestamp):
                        value = value.strftime('%Y-%m-%dT%H:%M:%S')  # format ISO
                    elif isinstance(value, str) and len(value) > 255:
                        value = value[:255]  # certains champs texte ont une limite
                    
                    # Ajout dans le dictionnaire
                    item_data[sharepoint_field] = value
            try:
                target_list.add_item(item_data)
            except Exception as e:
                print(f"⚠️ Erreur en ajoutant un élément : {e}")
                
        # 🔁 Tentative de commit avec gestion des erreurs 503
        MAX_RETRIES = 10
        RETRY_DELAY = 10  # secondes
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                ctx.execute_query()
                print(f"✅ Import terminé pour la liste '{list_name}'.")
                break  # Succès
            except Exception as e:
                if "503" in str(e):
                    print(f"⏳ SharePoint indisponible (503). Tentative {attempt}/{MAX_RETRIES}... Attente {RETRY_DELAY}s.")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"❌ Erreur critique lors de l'import : {e}")
                    raise



def vide_liste_sharepoint(ctx, target_list):
    """
    Vide une liste SharePoint en supprimant tous ses éléments, avec gestion des erreurs.
    :param ctx: ClientContext permettant d'avoir accès à la liste
    :param target_list: Liste SharePoint à vider 
    """
    page_size = 100
    total_deleted = 0
    total_failed = 0

    while True:
        items = target_list.items.top(page_size).get().execute_query()
        if not items:
            print("✅ Liste vide.")
            break

        print(f"🔄 Tentative de suppression de {len(items)} éléments...")
        for item in items:
            try:
                item.delete_object()
            except Exception as e:
                total_failed += 1
                print(f"⚠️ Erreur lors de la suppression de l'élément ID={item.properties.get('ID', '?')}: {e}")


        # 🔁 suppression des éléments de la liste avec gestion des erreurs 503
        MAX_RETRIES = 10
        RETRY_DELAY = 10  # secondes
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                ctx.execute_query()
                print(f"✅ Suppression réussie")
                break  # Succès
            except Exception as e:
                if "503" in str(e):
                    print(f"⏳ SharePoint indisponible (503). Tentative {attempt}/{MAX_RETRIES}... Attente {RETRY_DELAY}s.")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"❌ Erreur critique lors de la suppression : {e}")
                    raise

    print(f"✅ Suppression terminée. {total_deleted} supprimés, {total_failed} erreurs.")