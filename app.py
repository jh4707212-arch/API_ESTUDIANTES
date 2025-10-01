import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__)

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

@app.route('/estudiantes', methods=['GET'])
def get_estudiantes():
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