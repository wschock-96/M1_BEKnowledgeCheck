from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customers_bp
from .schemas import customer_schema, customers_schema
from app.models import Customer, db


@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()

    if existing_customer:
        return jsonify({"error": "Customer with this email already exists"}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201

@customers_bp.route('/', methods=['GET'])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    if customers:
        return customers_schema.jsonify(customers), 200
    return jsonify("message:" "no customers found"), 200

@customers_bp.route('//<int:id>', methods=['GET'])
def get_customer(id):
    customer = db.session.get(Customer, id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "customer id not found"}), 404

@customers_bp.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"error": "customer id not found"}), 404

    try:
        updated_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route('//<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"error": "customer id not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {id} deleted successfully"}), 200