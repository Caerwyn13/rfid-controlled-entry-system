import sqlite3
from flask import current_app
from flaskr.db import get_db

import sqlite3
from flask import current_app
from flaskr.db import get_db

def execute_sql_query(query, userid):
    """Execute the user-provided SQL query."""
    with current_app.app_context():
        db = get_db()

        # Prevent UPDATE queries
        if "UPDATE" in query.upper() and userid.lower() != 'admin':
            raise Exception("UPDATE queries are NOT allowed for security reasons.")

        try:
            # Execute the query
            cursor = db.execute(query)
            
            # If it's a SELECT query, fetch the results
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()

                # Convert each sqlite3.Row object to a tuple
                results = [tuple(row) for row in results] 

                # Restrict password view (prevent 'scrypt:...' from showing)
                for i in range(len(results)):
                    for j in range(len(results[i])):
                        value = results[i][j]
                        if isinstance(value, str) and value.strip().startswith("scrypt"):
                            results[i] = results[i][:j] + ("[REDACTED INFORMATION]",) + results[i][j+1:] 

            else:
                # For non-SELECT queries, commit changes and return the number of affected rows
                db.commit()
                results = f"{cursor.rowcount} rows affected."

        except sqlite3.Error as e:
            raise Exception(f"SQL error: {e}")
        
    return results

