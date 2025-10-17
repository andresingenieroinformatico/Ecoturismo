from flask import Flask, render_template, redirect, url_for, request, session, flash
from utils.login import login_required
from utils.phone_format import format_phone
from controller.user_controller import insert_user, is_exists
from flask_bcrypt import Bcrypt
from connection import connection

app = Flask(__name__, static_folder='static', template_folder='templates')
bcrypt = Bcrypt(app)
app.secret_key = "advpjsh"
supabase=connection()

def get_session_user_data():
    return {
        'primer_N': session.get('primer_N', 'Usuario'),
        'primer_A': session.get('primer_A', '')
    }

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        clave=request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(clave).decode('utf-8')
        data={
            "primer_nombre" : request.form.get('primer_N'),
            "segundo_nombre" : request.form.get('segundo_N', ''),
            "primer_apellido" : request.form.get('primer_A'),
            "segundo_apellido" : request.form.get('segundo_A', ''),
            "correo" : request.form.get('email'),
            "contrasena" : hashed_password,
            "cedula" : request.form.get('cedula'),
            "telefono" : format_phone(request.form.get('celular')),
            "tipo_usuario" : request.form.get('tipo_usu').lower()
        }

        if not all([data['primer_nombre'], 
                    data['primer_apellido'], 
                    data['cedula'], 
                    data['correo'], 
                    data['contrasena'], 
                    data['tipo_usuario'], 
                    data['telefono']]
                ):
            flash("Por favor, complete todos los campos obligatorios.", "error")
            return render_template('register.html')
        
        exists=is_exists(data['correo'],supabase)
        if exists['exists']:
            flash("Usuario no disponible.", "error")
            return render_template('register.html')

        try:
            insert_user(data,supabase)
            flash("Registro exitoso. Bienvenido!", "success")
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Error al registrarse", "error")
            print(e)
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tipo_usu = request.form.get('tipo_usu') 
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([tipo_usu, email, password]):
            flash("Por favor, complete todos los campos.", "error")
            return render_template('login.html')
        
        user=is_exists(email, supabase)
        print(user)
        if bcrypt.check_password_hash(user['data'][0]['contrasena'], password) and user['exists']:
            session['email'] = user['data'][0]['correo']
            session['primer_N'] = user['data'][0]['primer_nombre']
            session['primer_A'] = user['data'][0]['primer_apellido']
            session['tipo_usu'] = user['data'][0]['tipo_usuario']

            if session['tipo_usu'] == 'admin':
                return redirect(url_for('index_admin'))
            return redirect(url_for('index'))
        else:
            flash("Usuario, contraseña o rol incorrecto.", "error")

    return render_template('login.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/lugares')
@login_required
def lugares():
    return render_template('lugares.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/como_reservar')
def como_reservar():
    return render_template('como_reservar.html')

@app.route('/rutas_a_elegir')
@login_required
def rutas_a_elegir():
    return redirect(url_for('lugares'))

if __name__ == '__main__':
    app.run(debug=True)