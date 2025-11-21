"""
Gets the fname associated with the username to display a greting
"""


from flask import Blueprint, jsonify
from flaskr.db import get_db

bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/get_name/<username>")
def get_name(username):
    db = get_db()
    user = db.execute(
        "SELECT fname FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user is None:
        # Should not happen, but needs to be accounted for
        return jsonify({"error": "Name not found, please contact IT"})
    
    return jsonify({"username": username, "fname": user["fname"]})
