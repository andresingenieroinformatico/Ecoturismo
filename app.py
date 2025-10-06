from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask_bcrypt import Bcrypt
import random
from werkzeug.exceptions import NotFound
import pymysql
from itsdangerous import URLSafeSerializer as Serializer

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "advpjsh"

def get_db():
    if "db" not in g:
        try:
            g.db = pymysql.connect(
                host="localhost",
                user="root",
                password="12072022",
                database="sector_transporte",
                cursorclass=pymysql.cursors.DictCursor
            )
            g.cursor = g.db.cursor()
        except pymysql.MySQLError as err:
            raise Exception(f"Error al conectar a la base de datos: {err}")
    return g.db, g.cursor

app = Flask(__name__)


@app.route('/')
def pagina_principal():
    if 'email' in session:
        return redirect(url_for('base'))
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tipo_usu = request.form.get('tipo_usu') 
        email = request.form.get('email')
        password = request.form.get('password')
        if not tipo_usu or not email or not password:
            flash("Por favor, complete todos los campos.", "error")
            return render_template('login.html')
        try:
            db, cursor = get_db()
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and bcrypt.check_password_hash(user['password'], password):
                if user['tipo_usu'] == tipo_usu:
                    session['email'] = user['email']
                    session['primer_N'] = user['primer_N']
                    session['primer_A'] = user['primer_A']
                    session['tipo_usu'] = user['tipo_usu']
                    if user['tipo_usu'] == 'Administrador':
                        return redirect(url_for('index_admin'))
                    else:
                        return redirect(url_for('index'))
                else:
                    flash("El rol seleccionado no coincide con el registrado.", "error")
                    return render_template('login.html')
            else:
                flash("Rol, Usuario o contraseña incorrectos.", "error")
                return render_template('login.html')
        except pymysql.Error as e:
            flash(f"Error en la base de datos: {str(e)}", "error")
            return render_template('login.html')
    return render_template('login.html')
