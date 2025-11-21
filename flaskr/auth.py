from flask import (
    Blueprint, flash, render_template, request, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Register form for accounts
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (fname, lname, username, password) VALUES (?, ?, ?, ?)",
                    (fname, lname, username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
               error = 'This username already exists'
            else:
                error = 'Registered correctly!'
            
        flash(error)

    # GET request will render registration page
    return render_template('register.html')



# Validate credentials for login
@bp.route('/validate_credentials', methods=('POST',))
def validate_credentials():
    username = request.form['username']
    password = request.form['password']
    
    db = get_db()
    error = None

    # Query the user from the database by username
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if user is None or not check_password_hash(user['password'], password):
        error = 'Incorrect username or password'

    if error is None:
        # If validation passes, you can return a success message or status
        return jsonify({"message": "Validation successful", "status": "success"}), 200
    else:
        # If validation fails, return an error message
        return jsonify({"message": error, "status": "error"}), 400
