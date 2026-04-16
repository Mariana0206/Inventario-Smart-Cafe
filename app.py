from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

db_path = os.path.join(os.path.dirname(__file__), 'inventario.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "nombre": self.nombre, "tipo": self.tipo,
            "estado": self.estado, "area": self.area,
            "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d %H:%M:%S")
        }

with app.app_context():
    db.create_all()

@app.route('/devices', methods=['GET'])
def get_devices():
    return jsonify([d.to_dict() for d in Device.query.all()]), 200

@app.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.get_or_404(device_id)
    return jsonify(device.to_dict()), 200

@app.route('/devices', methods=['POST'])
def create_device():
    data = request.json
    if not data or not all(k in data and str(data[k]).strip() for k in ('nombre', 'tipo', 'estado', 'area')):
        abort(400, description="Campos vacíos")
    new = Device(nombre=data['nombre'], tipo=data['tipo'], estado=data['estado'], area=data['area'])
    db.session.add(new)
    db.session.commit()
    return jsonify(new.to_dict()), 201

@app.route('/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    device = Device.query.get_or_404(device_id)
    data = request.json
    device.nombre = data.get('nombre', device.nombre)
    device.tipo = data.get('tipo', device.tipo)
    device.estado = data.get('estado', device.estado)
    device.area = data.get('area', device.area)
    db.session.commit()
    return jsonify(device.to_dict()), 200

@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return jsonify({"message": "Eliminado"}), 200

if __name__ == '__main__':
    app.run(debug=True)