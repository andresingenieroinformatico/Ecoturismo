from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt
from supabase import create_client, Client
from dotenv import load_dotenv
import os
load_dotenv()

# Configuración de Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
# Configuración de Supabase
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(e)

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "advpjsh"

@app.route('/')
def base():
    return render_template('base.html')

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

        # Validación básica
        if not all([primer_N, primer_A, celular, email, cedula, tipo_usu, password]):
            flash("Por favor, complete todos los campos obligatorios.", "error")
            return render_template('register.html')

        # Formatear celular
        celular = celular.strip()
        if not celular.startswith('+57'):
            if celular.startswith('0'):
                celular = '+57' + celular[1:]
            elif celular.startswith('3'):
                celular = '+57' + celular
            else:
                celular = '+57' + celular  

        # Verificar si el correo ya existe
        user = supabase.table('usuarios').select('*').eq('correo', email).execute()
        if user.data:
            flash("El correo electrónico ya está registrado.", "error")
            return render_template('register.html')

        # Encriptar contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insertar usuario
        try:
            supabase.table('usuarios').insert({
                "primer_nombre": primer_N,
                "segundo_nombre": segundo_N,
                "primer_apellido": primer_A,
                "segundo_apellido": segundo_A,
                "correo": email,
                "contrasena": hashed_password,
                "cedula": cedula,
                "telefono": celular,
                "tipo_usuario": str(tipo_usu).lower()
            }).execute()

            session['email'] = email
            session['primer_N'] = primer_N
            session['primer_A'] = primer_A
            flash("Registro exitoso. Bienvenido!", "success")
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Error al registrarse: {str(e)}", "error")
            print(e)
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
            user = supabase.table('usuarios').select('*').eq('correo', email).execute()
            if not user.data:
                flash("Usuario no encontrado.", "error")
                return render_template('login.html')

            user = user.data[0]

            if bcrypt.check_password_hash(user['contrasena'], password):
                if user['tipo_usuario'] == tipo_usu.lower():
                    session['email'] = user['correo']
                    session['primer_N'] = user['primer_nombre']
                    session['primer_A'] = user['primer_apellido']
                    session['tipo_usu'] = user['tipo_usuario']

                    if user['tipo_usuario'] == 'admin':
                        return redirect(url_for('index_admin'))
                    else:
                        print('entro')
                        return redirect(url_for('index'))
                else:
                    flash("El rol seleccionado no coincide con el registrado.", "error")
            else:
                flash("Contraseña incorrecta.", "error")

        except Exception as e:
            flash(f"Error en la base de datos: {str(e)}", "error")
            print(e)

    return render_template('login.html')

@app.route('/index')
def index():
    if 'email' not in session:
        flash("Por favor, inicia sesión para continuar.", "error")
        return redirect(url_for('login'))
    usuario = {
        'primer_N': session.get('primer_N', 'Usuario'),
        'primer_A': session.get('primer_A', '')
    }
    return render_template('index.html', usuario=usuario)

@app.route('/lugares')
def rlugares():
    if 'email' not in session:
        flash("Por favor, inicia sesión para continuar.", "error")
        return redirect(url_for('login'))
    usuario = {
        'primer_N': session.get('primer_N', 'Usuario'),
        'primer_A': session.get('primer_A', '')
    }
    return render_template('lugares.html', usuario=usuario)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/lugares')
def lugares():
    return render_template('lugares.html')

@app.route('/como_reservar')
def como_reservar():
    return render_template('como_reservar.html')

if __name__ == '__main__':
    app.run(debug=True)
