import sqlite3
from os import path
from flask import Flask
from flask import render_template
from flask import request

from datetime import datetime
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


def retourne_les_donnees(limit: int = 10) -> list:
    """Retourne les derniers enregistrements de la base de données.
    Renvoie une liste de dictionnaire."""
    conn = get_db_connection()
    cur = conn.cursor()
    req_select = """SELECT *
    FROM iot_data
    ORDER BY temps desc
    LIMIT ?"""
    result = cur.execute(req_select, (limit,)).fetchall()
    conn.close()
    return result


def inserer_un_log(cle: str, valeur: str) -> None:
    """Retourne les derniers enregistrements de la base de données.
    Renvoie une liste de dictionnaire."""
    temps = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cur = conn.cursor()
    requete_import = "INSERT INTO iot_data (temps, cle, valeur) VALUES (?, ?, ?)"
    cur.execute(requete_import, (temps, cle, valeur))
    conn.commit()
    conn.close()
    return "OK"


@app.route("/get")
def retrieve_data():
    if request.args:
        for cle, valeur in request.args.items():
            inserer_un_log(cle, valeur)
    # Afficher les dernières données
    return render_template(
        "get_data.html",
        lignes=retourne_les_donnees()
    )


@app.route("/post")
def store_data():
    retour = ""
    for arg in request.args:
        code_retour = inserer_un_log(arg, request.args[arg])
        retour += f'<p>Insertion de "{arg}" = {code_retour}</p>\n'
    return retour
