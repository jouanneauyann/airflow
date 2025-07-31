import pymysql #type: ignore

def get_connexion_glpi(body):
    conn = pymysql.connect(**body)
    return conn
