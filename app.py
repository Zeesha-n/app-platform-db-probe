import os

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def health():
    return jsonify(
        ok=True,
        message="Database identity probe is running",
    )


@app.get("/identity")
def identity():
    database_url = os.environ.get("SFIP_DATABASE_URL")

    if not database_url:
        return jsonify(
            ok=False,
            error="SFIP_DATABASE_URL is not configured",
        ), 500

    try:
        with psycopg.connect(database_url, connect_timeout=10) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        current_database(),
                        current_user
                    """
                )
                database, role = cursor.fetchone()

        # Deliberately return only database and role identity.
        # Never return or log the connection URL.
        return jsonify(
            ok=True,
            database=database,
            role=role,
        )

    except Exception as exc:
        # Do not include the exception message because some database
        # errors contain host, database, or username information.
        return jsonify(
            ok=False,
            error_type=type(exc).__name__,
        ), 500