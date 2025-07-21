from . import mechanics_bp
from app.models import Mechanic, db
from flask import jsonify, request, current_app
from .schemas import mechanic_schema, mechanics_schema, login_schema
from app.extensions import limiter, cache
from sqlalchemy import select
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from app.util.auth import encode_auth_token


# login route
@mechanics_bp.route('/login', methods=['POST'])
def login_mechanic():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == creds['email'])
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and check_password_hash(mechanic.password, creds['password']):
        print("Login SECRET_KEY:", current_app.config['SECRET_KEY']) ###
        token = encode_auth_token(mechanic.id, role='mechanic')
        return jsonify({"message": "Login successful", "token": token, "user" : mechanic_schema.dump(mechanic)}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# Mechanic routes
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().all()

    if existing_mechanic:
        return jsonify({"error": "Mechanic with this email already exists"}), 400
    
    mechanic_data['password'] = generate_password_hash(mechanic_data['password'])
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=30)
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic id not found"}), 404

    try:
        updated_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        setattr(mechanic, key, value)

    if 'password' in updated_data:
        mechanic.password = generate_password_hash(updated_data['password'])

    db.session.commit()

    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "customer id not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {id} deleted successfully"}), 200

