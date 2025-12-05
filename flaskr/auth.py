from flask import (
    Blueprint, flash, render_template, request, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

departments = {
    1: 'Administration',
    2: 'Marketing',
    3: 'Purchasing',
    4: 'Human Resources',
    5: 'Shipping',
    6: 'IT',
    7: 'Public Relations',
    8: 'Sales',
    9: 'Executive',
    10: 'Finance',
    11: 'Accounting',
    12: 'Treasury',
    13: 'Shareholder Services',
    14: 'Manufacturing',
    15: 'Contracting',
    16: 'Operational Security',
    17: 'NOC',
    18: 'Helpdesk',
    19: 'Recruiting'
}

def get_key_by_value(department_dict, value):
    for key, val in department_dict.items():
        if val == value:
            return key
    return None  # Return None if the value is not found

# Register form for accounts
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        department = request.form.get('department')
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
                    "INSERT INTO users (fname, lname, username, password, department_id) VALUES (?, ?, ?, ?, ?)",
                    (fname.lower(), lname.lower(), username, generate_password_hash(password), get_key_by_value(departments, department.title()))
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
