import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv 
import logging # Importamos la librería de logging

# Configurar logging para ver errores detallados en Render
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno (DATABASE_URL)
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos (usa la variable de entorno de Render)
# NOTA: Asegúrate de que esta URL tiene el 'postgresql://' y no 'postgres://'
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
    try:
        estudiantes = Estudiante.query.all()
        return render_template('index.html', estudiantes=estudiantes)
    except Exception as e:
        logging.error(f"Error al cargar la tabla de index: {e}")
        return "Error al cargar los datos de la base de datos.", 500

# Ruta GET para mostrar el formulario de creación
@app.route('/estudiantes/create', methods=['GET'])
def create_estudiante_web():
    # Necesita un archivo 'create_estudiante.html' en la carpeta 'templates/'
    return render_template('create_estudiante.html')

# Ruta POST para insertar un estudiante desde el formulario web
@app.route('/insert', methods=['POST'])
def insert_web():
    data = request.form
    try:
        # Asegurar que el semestre es un entero
        semestre_int = int(data['semestre'])
    except ValueError:
        return "El campo 'semestre' debe ser un número entero.", 400

    nuevo_estudiante = Estudiante(
        no_control = data['no_control'],
        nombre = data['nombre'],
        ap_paterno = data['ap_paterno'],
        ap_materno = data['ap_materno'],
        semestre = semestre_int
    )
    try:
        db.session.add(nuevo_estudiante)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al insertar estudiante web: {e}")
        return f"Error al insertar estudiante web (posible duplicado o BD caída): {e}", 500

# Ruta POST para eliminar un estudiante web
@app.route('/estudiantes/delete/<no_control>', methods=['POST'])
def delete_estudiante_web(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return "Estudiante no encontrado para eliminar", 404
    try:
        db.session.delete(estudiante)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al eliminar estudiante web: {e}")
        return f"Error al eliminar estudiante web: {e}", 500

# Ruta GET y POST para actualizar un estudiante web (RUTA DE PRUEBA/PLACEHOLDER)
@app.route('/estudiantes/update/<no_control>', methods=['GET', 'POST'])
def update_estudiante_web(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return "Estudiante no encontrado para actualizar", 404

    if request.method == 'POST':
        # Esta es la lógica para procesar el formulario de actualización
        if 'nombre' in request.form:
             estudiante.nombre = request.form['nombre']
        # Añade aquí más campos si implementas el formulario de actualización...
        
        try:
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error al actualizar estudiante web: {e}")
            return f"Error al actualizar estudiante web: {e}", 500
    
    # En el caso de GET, deberías renderizar un formulario con los datos prellenados
    # return render_template('update_estudiante.html', estudiante=estudiante) 
    return f"Página de actualización para {estudiante.nombre} (No Control: {no_control}). Necesitas implementar el formulario de actualización.", 200


# -----------------------------------------------
# 2. RUTAS DE LA API REST (Maneja el JSON)
# -----------------------------------------------

# RUTA CRÍTICA CORREGIDA PARA ASEGURAR JSON
@app.route('/estudiantes', methods=['GET'])
def get_estudiantes():
    try:
        estudiantes = Estudiante.query.all()
        lista_estudiantes = []
        for estudiante in estudiantes:
            # Usamos 'or '' ' para prevenir errores si algún campo de texto es NULL en la BD
            # aunque esté definido como String(100) en el modelo.
            lista_estudiantes.append({
                'no_control': estudiante.no_control or '',
                'nombre': estudiante.nombre or '',
                'ap_paterno': estudiante.ap_paterno or '',
                'ap_materno': estudiante.ap_materno or '',
                'semestre': estudiante.semestre,
            })
        return jsonify(lista_estudiantes)
    except Exception as e:
        # Si esta ruta falla, mostrará este JSON con el error para diagnosticar.
        logging.error(f"FALLA FATAL en API GET /estudiantes: {e}")
        return jsonify({'msg': 'Error en el servidor al obtener lista de API JSON', 'detail': str(e)}), 500

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