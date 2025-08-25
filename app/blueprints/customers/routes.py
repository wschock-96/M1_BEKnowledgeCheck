from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customers_bp
from .schemas import customer_schema, customers_schema
from app.models import Customer, db
from app.extensions import limiter, cache


@customers_bp.route('/', methods=['POST'])
@limiter.limit("15 per hour", override_defaults=True)
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
@cache.cached(timeout=30)
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.session.paginate(query, page=page, per_page=per_page)
        
        return customers_schema.jsonify(customers), 200 

    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()

        if customers:
            return customers_schema.jsonify(customers), 200
        return jsonify("message:" "no customers found"), 200

@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    customer = db.session.get(Customer, id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "customer id not found"}), 404

@customers_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("15 per hour", override_defaults=True)
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

@customers_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("3 per hour", override_defaults=True)
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"error": "customer id not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {id} deleted successfully"}), 200

@customers_bp.route("/most-valuable", methods=['GET'])
def get_most_valuable():
    customers = db.session.execute(select(Customer)).scalars().all()
    customers.sort(key=lambda customer: len(customer.tickets), reverse=True)
    return customers_schema.jsonify(customers), 200

@customers_bp.route("/search", methods=['GET'])
def search_customers():
    email = request.args.get('email')

    query = select(Customer).where(Customer.email.ilike(f"%{email}%"))
    customer = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customer)

    