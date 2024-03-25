import sqlite3
from os import path
from flask import Flask
from flask import request

from datetime import date
from time import time


PROJECT_ROOT = path.dirname(path.realpath(__file__))
DATABASE_PATH = path.join(PROJECT_ROOT, "database.db")

__VERSION__ = "0.1"
base_info = {
    "version": __VERSION__,
}

app = Flask(__name__)


def debug_var(var):
    """pour débuguer les variables."""
    print("=============== DEBUG ==============")
    print(f"type(var) = {type(var)}")
    print(f"var = {var}")
    print("================ FIN ===============")


def get_db_connection():
    """Renvoie une connexion à la base de données."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def retourne_les_donnees() -> list:
    """Retourne les derniers enregistrements de la base de données.
    Renvoie une liste de dictionnaire."""
    conn = get_db_connection()
    req_select = """SELECT *
    FROM iot_data
    ORDER BY temps desc
    LIMIT 10"""
    result = conn.execute(req_select).fetchall()
    print(result)
    conn.close()
    return result


def inserer_un_log(cle: str, valeur: str) -> None:
    """Retourne les derniers enregistrements de la base de données.
    Renvoie une liste de dictionnaire."""
    temps = date.fromtimestamp(time()).strftime("YYYY-MM-DD HH:MM:SS")
    conn = get_db_connection()
    cur = conn.cursor()
    requete_import = "INSERT INTO iot_data (temps, cle, valeur) VALUES (?, ?, ?)"
    cur.execute(requete_import, (temps, cle, valeur))
    conn.commit()
    conn.close()
    return "OK"


@app.route("/get")
def retrieve_data():
    retour = ""
    if request.args:
        retour = f"J'ai bien reçu {request.args}\n"
    else:
        retour = (
            "<p>Je n'ai rien reçu, donc je te renvoie les 10 dernières entrées</p>\n"
        )
        lignes = retourne_les_donnees()
        # TODO : finir ça.
        for ligne in lignes:
            print(f"ligne = {ligne}")
            print(f"temps = {ligne['temps']}")
            print(f"cle = {ligne['cle']}")
            print(f"valeur = {ligne['valeur']}")
            retour += f"<p>ligne = {ligne}</p>\n"
    return retour


@app.route("/post")
def store_data():
    retour = ""
    for arg in request.args:
        code_retour = inserer_un_log(arg, request.args[arg])
        retour += f'<p>Insertion de "{arg}" = {code_retour}</p>\n'
    return retour
