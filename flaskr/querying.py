import sqlite3

from flask import current_app

from . import db


def execute_sql_query(query):
    """Execute the user-provided SQL query."""
    with current_app.app_context():
        conn = db.get_db()
        cursor = conn.cursor()

        if "UPDATE" in query.upper():
            return "UPDATE queries are NOT allowed"
        
        try:
            # Execute the user query
            cursor.execute(query)
            results = cursor.fetchall()  # Fetch all results
        except sqlite3.Error as e:
            raise Exception(f"SQL error: {e}")
        finally:
            conn.close()

    return results
