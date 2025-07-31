# 🏗️ Data Platform – Ingestion - Transformation - Restitution

Ce projet met en œuvre une **data plateforme** basée sur Airflow, Python, Snowflake, DBT et QlikSense.  
Il permet l’ingestion automatisée de données depuis plusieurs sources (APIs, bases de données, fichiers plats), leur transformation avec DBT, puis leur exposition à notre outil de visualisation : QlikSense.

---

## 🏠 Architecture Globale

        [Sources externes : API, SQL, SharePoint]
                        │
                        ▼
             ┌─────────────────────┐
             │ Airflow + Python DAGs
             └─────────────────────┘
                        │
                        ▼
      [Fichiers temporaires créés sur le serveur airflow]
                        │
                        ▼
            [Ingestion dans Snowflake ]
                        │
                        ▼
             [Transformation avec DBT]
                        │
                        ▼
            [Visualisation via QlikSense]

## 📂 Organisation du répertoire Globale
```
├── config/ # Fichiers de configuration permettant de gérer la connexion à Snowflake et les paramètres par défaut d'un DAG
│ ├── airflow.cfg
│ ├── config_snowflake.json
│ ├── default_args.py
│ ├── rsa_key.pem
│ └── rsa_key.pub
│ 
├── dags/ # Fichiers DAG Airflow (un par source ou type d'ingestion)
│ ├── ingestion_<source>.py # dags d'ingestion d'une source vers Snowflake
│ ├── actualisation_liste_sharepoint.py # dag divers permettant de mettre à jour des listes dans SharePoint
│ └── log_maintenance.py 
│
├── scripts/ # Scripts Python d’ingestion et logique métier
│ └── ingestion/
│   ├── ingestion_api.py
│   ├── ingestion_sql.py
│   ├── ingestion_sharepoint.py
│   ├── module_global.py
│ └── <source>/
│   └── config_<source>.yaml # Fichier YAML propre à chaque source
│
├── data/ # Données temporaires extraites avant ingestion dans Snowflake
│ └── <source>/<requete>/<fichiers>.<extension> (uniquement CSV, JSON ou PARQUET)
│
├── logs/ # Logs d’exécution Airflow et Python
│
├── zabbix/ # Zabbix monitore le bon fonctionnement des dags de façon à remonter une alerte en cas de fichier présent dans ce dossier
│
└── README.md # Présentation du projet (ce fichier)
```

---

## ⚙️ Fonctionnement d’un DAG d'ingestion

Chaque DAG d'ingestion suit la logique suivante :

1. **Connexion à la source** (API, BDD, SharePoint)
2. **Exécution des requêtes** (configurées dans un fichier `yaml`)
3. **Écriture locale des résultats** (CSV/JSON/PARQUET dans `/data`)
4. **Chargement dans Snowflake** (Import des requêtes dans un stage)

Les scripts Python sont **génériques** et contrôlés par des **fichiers YAML** propres à chaque source. Ainsi, pour chaque type de source, il y a un script python qui appel le fichier de configuration YAML associée à la source.

---

## 🛠️ Technologies utilisées

1. **Airflow** : Orchestration des pipelines
2. **Python** : Scripts d’extraction & ingestion
3. **Snowflake** : Stockage & compute des données
4. **DBT** : Transformation & modélisation des données
5. **QlikSense** : Visualisation et reporting