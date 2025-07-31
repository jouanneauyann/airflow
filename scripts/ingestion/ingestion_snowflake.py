import os
from datetime import datetime
import snowflake.connector #type: ignore
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import module_global # type: ignore
from cryptography.hazmat.primitives import serialization

def ingestion_snowflake(source_name):
    """
    Fonction permettant de pousser les fichiers extraits dans le stage snowflake
    """
    config_yaml = module_global.get_config_yaml(source_name)
    conn = connect_snowflake()
    for method in config_yaml["list_method"]:
        nom_requete = list(method.keys())[0]
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, '..', '..','data',source_name,f"{nom_requete}")
        schema_name = "SRC_" + source_name
        put_file_snowflake(data_dir, nom_requete, "ingestion_stage", schema_name, conn)


def connect_snowflake():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    conf_snowflake = os.path.join(current_dir, '..', '..','config','config_snowflake.json')
    with open(conf_snowflake, "r", encoding="utf-8") as file:
        config = json.load(file) 
    
    private_key_bytes = get_private_key()
    conn = snowflake.connector.connect(
        user=config['user'],
        account=config['account'],
        private_key=private_key_bytes,
        warehouse=config['warehouse'],
        database=config['database'],
        schema=config['schema'],
        role=config['role'],
        authenticator=config['authenticator']
    )
    return conn

def get_private_key():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    private_key_path = os.path.join(current_dir, '..', '..','config','rsa_key.pem')
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return private_key_bytes

def put_file_snowflake(data_dir, data_name, stage_name, schema_name, conn):
    cursor = conn.cursor()
    cursor.execute("USE ROLE PROD_OWNER")
    cursor.execute("USE DATABASE PROD_BI")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS " + schema_name)
    cursor.execute("USE SCHEMA " + schema_name)
    cursor.execute("CREATE STAGE IF NOT EXISTS " + stage_name)
    data_dir = data_dir.replace("\\","/")
    # Les fichiers à pousser dans le stage Snowflake doivent être au format CSV/JSON/PAQUET
    cursor.execute(f"PUT 'file://{data_dir}/*' @{schema_name}.{stage_name}/last_ingestion/{data_name} AUTO_COMPRESS=FALSE OVERWRITE=TRUE PARALLEL=16;")
    annee = datetime.now().year
    mois = datetime.now().month
    jour = datetime.now().day
    cursor.execute("CREATE STAGE IF NOT EXISTS " + stage_name)
    cursor.execute(f"PUT 'file://{data_dir}/*' @{schema_name}.{stage_name}/{annee}/{mois}/{jour}/{data_name} AUTO_COMPRESS=FALSE OVERWRITE=TRUE PARALLEL=16;")