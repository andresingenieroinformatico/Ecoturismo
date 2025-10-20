from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt
import json
from utils.login import login_required
from utils.phone_format import format_phone
from controller.user_controller import insert_user, is_exists, update_profile
from controller.reservas_controller import get_data, make_reservation
from connection import connection

app = Flask(__name__, static_folder='static', template_folder='templates')
bcrypt = Bcrypt(app)
app.secret_key = "advpjsh"
supabase=connection()

def get_session_user_data():
    return {
        'primer_nombre': session.get('primer_nombre'),
        'segundo_nombre': session.get('segundo_nombre'),
        'primer_apellido': session.get('primer_apellido'),
        'segundo_apellido': session.get('segundo_apellido'),
        'cedula': session.get('cedula'),
        'correo': session.get('correo'),
        'telefono': session.get('telefono')
    }

@app.context_processor
def inject_user():
    user = get_session_user_data()
    return dict(user=user)

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
        if bcrypt.check_password_hash(user['data'][0]['contrasena'], password) and user['exists']:
            
            session['id'] = user['data'][0]['id']
            session['primer_nombre'] = user['data'][0]['primer_nombre']
            session['segundo_nombre'] = user['data'][0]['segundo_nombre']
            session['primer_apellido'] = user['data'][0]['primer_apellido']
            session['segundo_apellido'] = user['data'][0]['segundo_apellido']
            session['cedula'] = user['data'][0]['cedula']
            session['correo'] = user['data'][0]['correo']
            session['telefono'] = user['data'][0]['telefono']
            session['tipo_usuario'] = user['data'][0]['tipo_usuario']

            if user['data'][0]['tipo_usuario'] == 'admin':
                return redirect(url_for('index_admin'))
            return redirect(url_for('index'))
        else:
            flash("Usuario, contraseña o rol incorrecto.", "error")

    return render_template('login.html')

@app.route('/actualizar', methods=['GET', 'POST'])
def actualizar():
    if request.method == 'POST':
        id=session.get('id')
        data={
            "primer_nombre" : request.form.get('primer_N'),
            "segundo_nombre" : request.form.get('segundo_N', ''),
            "primer_apellido" : request.form.get('primer_A'),
            "segundo_apellido" : request.form.get('segundo_A', ''),
            "correo" : request.form.get('email'),
            "cedula" : request.form.get('cedula'),
            "telefono" : format_phone(request.form.get('celular'))
        }

        success=update_profile(supabase, data, id)

        if success:
            flash("Usuario guardado correctamente.", "success")
            return redirect(url_for('index'))
        else:
            flash("Error al actualizar.", "error")

    return render_template('actualizar_perfil.html')

@app.route('/reservar', methods=['GET', 'POST'])
@login_required
def reservar():
    if request.method == 'POST':

        total_str = request.form.get('total', '0')

        # 🔧 Elimina símbolos de moneda y cambia comas por puntos
        total_limpio = (
            total_str.replace('$', '')
                     .replace(' ', '')
                     .replace('.', '')
                     .replace(',', '.')
        )

        total = float(total_limpio)
        data={
            'usuario_id':session.get('id'),
            "actividad_id" : request.form.get('actividad_id'),
            "fecha_reserva" : request.form.get('fecha_reserva'),
            "cantidad_personas" : request.form.get('cantidad_personas'),
            "estado" : 'pendiente',
            "total" : total
        }
        make_reservation(supabase, data)

    pagedata=get_data(supabase)
    pagedata_json = json.dumps(pagedata, default=str)
    return render_template('hacer_reserva.html', data=pagedata,  data_json=pagedata_json)

@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('base'))

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/lugares')
def lugares():
    return render_template('lugares.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/vehiculos')
def vehiculos():
    return render_template('vehiculos.html')

@app.route('/como_reservar')
def como_reservar():
    return render_template('como_reservar.html')

@app.route('/rutas_a_elegir')
def rutas_a_elegir():
    return redirect(url_for('lugares'))

@app.route('/perfil')
@login_required
def perfil():
    return render_template('mi_perfil.html')

if __name__ == '__main__':
    app.run(debug=True)