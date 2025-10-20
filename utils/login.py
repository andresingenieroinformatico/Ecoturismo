from functools import wraps
from flask import  redirect, url_for, flash, session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'correo' not in session:
            flash("Por favor, inicia sesión para continuar.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function