# Présentation des DAGS

## Actualise_liste_sharepoint

Ce DAG Airflow permet d’actualiser automatiquement des listes SharePoint à partir d’un fichier Excel source. Il est conçu pour être utilisé dans le contexte de la gestion RH, mais peut être adapté à d’autres besoins.

### Fonctionnement
1. Lecture du fichier Excel
    Le DAG lit le fichier SourcesListesSharePoint.xlsx situé dans le dossier excel.
    Chaque feuille du fichier correspond à une liste SharePoint à mettre à jour.

2. Mapping des feuilles Excel vers les listes SharePoint
    Le mapping est défini dans le script :

```
mapping = {
    "ESAT": "ESAT",
    "INTERIM": "SalariesFacilit",
    "NDF": "Salaries"
}
```

Chaque clé est le nom de la feuille Excel, chaque valeur le nom de la liste SharePoint cible.

3. Authentification SharePoint
    Les identifiants et l’URL du site SharePoint sont récupérés via les variables Airflow :
    - sharepoint_site_rh
    - sharepoint_username
    - sharepoint_password

4. Actualisation des listes
    Pour chaque feuille du fichier Excel, le DAG :

    - Vide la liste SharePoint cible
    - Importe les données de la feuille dans la liste

### Planification
Horaire : Tous les jours à 3h30 du matin 
Tags : sharepoint_grh
Catchup : Désactivé (catchup=False)

### Fichiers et scripts utilisés
- DAG : actualise_liste_sharepoint.py
- Script d’ingestion SharePoint : ingestion_sharepoint.py
- Script d’actualisation : actualisation_liste_sharepoint.py
- Fichier Excel source : SourcesListesSharePoint.xlsx

### Personnalisation
- Pour exclure une liste du rechargement, il suffit de commenter la ligne correspondante dans le mapping.
- Le fichier Excel source doit contenir une feuille pour chaque liste à actualiser, avec des colonnes correspondant aux champs SharePoint.
