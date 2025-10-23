from flask import Blueprint, request, render_template
import sqlite3

from . import db

bp = Blueprint('query', __name__, url_prefix='/queries')



 # Route for submitting custom SQL query
@bp.route('/execute-query', methods=['GET', 'POST'])
def execute_query():
    results = None
    error = None
    
    if request.method == 'POST':
        user_query = request.form['sql_query']
        
        try:
            results = execute_sql_query(user_query)
        except Exception as e:
            error = str(e)

    return render_template('execute_query.html', results=results, error=error)


def execute_sql_query(query):
    """Execute the user-provided SQL query."""
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
