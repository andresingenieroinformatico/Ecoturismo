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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        primer_N = request.form.get('primer_N')
        segundo_N = request.form.get('segundo_N', '')
        primer_A = request.form.get('primer_A')
        segundo_A = request.form.get('segundo_A', '')
        celular = request.form.get('celular')
        email = request.form.get('email')
        cedula = request.form.get('cedula')
        tipo_usu = request.form.get('tipo_usu')
        password = request.form.get('password')
        if not all([primer_N, primer_A, celular, email, cedula, tipo_usu, password]):
            flash("Por favor, complete todos los campos obligatorios.", "error")
            return render_template('register.html')
        celular = celular.strip()
        if not celular.startswith('+57'):
            if celular.startswith('0'):
                celular = '+57' + celular[1:]
            elif celular.startswith('3'):
                celular = '+57' + celular
            else:
                celular = '+57' + celular  
        db, cursor = get_db()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("El correo electrónico ya está registrado.", "error")
            return render_template('register.html')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            cursor.execute(
                "INSERT INTO usuarios (primer_N, segundo_N, primer_A, segundo_A, celular, email, cedula, tipo_usu, password) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (primer_N, segundo_N, primer_A, segundo_A, celular, email, cedula, tipo_usu, hashed_password)
            )
            db.commit()
            session['email'] = email
            session['primer_N'] = primer_N
            session['primer_A'] = primer_A
            flash("Registro exitoso. Bienvenido!", "success")
            return redirect(url_for('login'))
        except pymysql.Error as e:
            db.rollback()
            flash(f"Error al registrar: {str(e)}", "error")
            return render_template('register.html')
    return render_template('register.html')


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

if __name__ == '__main__':
    app.run(debug=True)