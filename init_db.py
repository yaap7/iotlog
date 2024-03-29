#!/usr/bin/env python3

import sqlite3


def main():
    """main function"""
    connection = sqlite3.connect("database.db")
    # Regénération du schéma de la base de données
    with open("schema.sql", encoding="utf-8") as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()
