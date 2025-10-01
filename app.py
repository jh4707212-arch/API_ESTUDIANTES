import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv 

# Cargar variables de entorno (DATABASE_URL)
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos (usa la variable de entorno de Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    no_control = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100))
    ap_paterno = db.Column(db.String(100))
    ap_materno = db.Column(db.String(100))
    semestre = db.Column(db.Integer)

# -----------------------------------------------
# 1. RUTAS DEL CRUD WEB (Maneja la Interfaz HTML)
# -----------------------------------------------

# Ruta Raíz: Muestra la tabla de estudiantes (Web)
@app.route('/')
def index():
    estudiantes = Estudiante.query.all()
    # Necesitas tener un archivo 'index.html' en la carpeta 'templates/'
    return render_template('index.html', estudiantes=estudiantes)

# Ruta de Inserción Web
@app.route('/insert', methods=['POST'])
def insert_web():
    # Nota: Este es un ejemplo. Debes adaptar los campos de 'request.form'
    # según lo que tu formulario HTML (insert.html) envíe.
    data = request.form
    nuevo_estudiante = Estudiante(
        no_control = data['no_control'],
        nombre = data['nombre'],
        ap_paterno = data['ap_paterno'],
        ap_materno = data['ap_materno'],
        semestre = int(data['semestre']) # Asegurar que es un entero
    )
    try:
        db.session.add(nuevo_estudiante)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception:
        db.session.rollback()
        # En una app real, aquí se manejaría un error
        return "Error al insertar estudiante web", 500

# Añadir aquí las rutas de update y delete del CRUD web (si las tenías)
# ...

# -----------------------------------------------
# 2. RUTAS DE LA API REST (Maneja el JSON)
# -----------------------------------------------

@app.route('/estudiantes', methods=['GET'])
def get_estudiantes():
    # Devuelve el listado completo en JSON
    estudiantes = Estudiante.query.all()
    lista_estudiantes = []
    for estudiante in estudiantes:
        lista_estudiantes.append({
            'no_control': estudiante.no_control,
            'nombre': estudiante.nombre,
            'ap_paterno': estudiante.ap_paterno,
            'ap_materno': estudiante.ap_materno,
            'semestre': estudiante.semestre
        })
    return jsonify(lista_estudiantes)

@app.route('/estudiantes/<no_control>', methods=['GET'])
def get_estudiante(no_control):
    # Devuelve un estudiante por No. Control en JSON
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify({'msg': 'Estudiante no encontrado'}), 404
    return jsonify({
        'no_control': estudiante.no_control,
        'nombre': estudiante.nombre,
        'ap_paterno': estudiante.ap_paterno,
        'ap_materno': estudiante.ap_materno,
        'semestre': estudiante.semestre,
    })

@app.route('/estudiantes', methods=['POST'])
def insert_estudiante():
    # Inserta un estudiante a través de la API (JSON payload)
    data = request.get_json()
    if not all(k in data for k in ('no_control', 'nombre', 'ap_paterno', 'ap_materno', 'semestre')):
        return jsonify({'msg': 'Faltan campos obligatorios'}), 400
        
    nuevo_estudiante = Estudiante(
        no_control = data['no_control'],
        nombre = data['nombre'],
        ap_paterno = data['ap_paterno'],
        ap_materno = data['ap_materno'],
        semestre = data['semestre']
    )
    
    try:
        db.session.add(nuevo_estudiante)
        db.session.commit()
        return jsonify({'msg': 'Alumno agregado correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Error al agregar alumno', 'detail': str(e)}), 500

@app.route('/estudiantes/<no_control>', methods=['DELETE'])
def delete_estudiante(no_control):
    # Elimina un estudiante por No. Control a través de la API
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify({'msg': 'Estudiante no encontrado'}), 404
    try:
        db.session.delete(estudiante)
        db.session.commit()
        return jsonify({'msg': 'Estudiante eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Error al eliminar estudiante', 'detail': str(e)}), 500

@app.route('/estudiantes/<no_control>', methods=['PATCH'])
def updateestudiante(no_control):
    # Actualiza parcialmente un estudiante por No. Control a través de la API
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify({'msg': 'Estudiante no encontrado'}), 404
    data = request.get_json()

    if "nombre" in data:
        estudiante.nombre = data['nombre']
    if "ap_paterno" in data:
        estudiante.ap_paterno = data['ap_paterno']
    if "ap_materno" in data:
        estudiante.ap_materno = data['ap_materno']
    if "semestre" in data:
        estudiante.semestre = data['semestre']

    try:
        db.session.commit()
        return jsonify({'msg': 'Estudiante actualizado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Error al actualizar estudiante', 'detail': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)