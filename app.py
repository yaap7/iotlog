#!/usr/bin/env python3

"""
Simple flask application to store and show simple "key/value" data
"""

import json
import re
import sqlite3

from datetime import datetime
from os import path
from time import time

import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.utils import PlotlyJSONEncoder

from flask import Flask
from flask import render_template
from flask import request


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


def create_graph(key_regexes: list) -> PlotlyJSONEncoder:
    """Returns a JSON-encoded plotly object representing the graph of the data gathered"""
    # TODO : réparer cette fonction pour autoriser l'affichage de plusieurs lignes sur un même graphe.
    # Exemple : température et humidité sur un même graphe
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    print(f"fig = {fig}")
    print(f"key_regexes = {key_regexes}")
    i = 0
    for key_regex in key_regexes:
        regex = re.compile(key_regex)
        plots = []
        for line in retourne_les_donnees(limit=1000):
            if regex.fullmatch(line["cle"]):
                plots.append((line["temps"], line["valeur"]))

        x = [i[0] for i in plots]
        y = [float(i[1]) for i in plots]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                name=key_regex,
            ),
            secondary_y=(i % 2 == 1),
        )
        i += 1

    # Set x-axis title
    fig.update_xaxes(title_text="Time")

    # Set y-axes titles
    fig.update_yaxes(title_text="Temperature", secondary_y=False)
    fig.update_yaxes(title_text="Humidity", secondary_y=True)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


@app.route("/")
@app.route("/get")
def get_data():
    """Get data and print them in a small HTML page without anything fancy"""
    limit = 10
    if "limit" in request.args:
        limit = request.args["limit"]
    # Afficher les dernières données
    return render_template("get_data.html", lignes=retourne_les_donnees(limit=limit))


@app.route("/post")
def store_data():
    """Simply store each data got in argument and print a simple return message."""
    retour = ""
    for arg in request.args:
        code_retour = inserer_un_log(arg, request.args[arg])
        retour += f'<p>Insertion de "{arg}" = {code_retour}</p>\n'
    return retour


@app.route("/graph")
def print_graph():
    """Simply put a simple graph in an almost empty web page"""
    key_regexes = list(value for value in request.args.getlist("key"))
    if len(key_regexes) < 1:
        return render_template("empty.html")
    graph = create_graph(key_regexes)
    return render_template("print_graph.html", graph=graph)
