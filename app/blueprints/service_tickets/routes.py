from . import service_tickets_bp
from app.models import ServiceTicket, Customer, Mechanic, db
from flask import jsonify, request
from .schemas import service_ticket_schema, service_tickets_schema
from sqlalchemy import select
from marshmallow import ValidationError
from app.blueprints.mechanics.schemas import mechanics_schema

@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer = db.session.get(Customer, service_ticket_data['customer_id'])
    if not customer:
        return jsonify({"error": f"Customer {id} not found"}), 404

    new_service_ticket = ServiceTicket(**service_ticket_data)
    db.session.add(new_service_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_service_ticket), 201

@service_tickets_bp.route('/<int:ticket_id>/add-mechanic/<int:mechanic_id>', methods=['PUT'])
def add_mechanic_to_ticket(ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if service_ticket and mechanic:
        if mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({"message": f"Successfully added Mechanic {mechanic.name} to ticket {ticket_id}",
                            "tickets": service_ticket_schema.dump(service_ticket),
                            "mechanics": mechanics_schema.dump(service_ticket.mechanics)}), 200
        return jsonify({"error": "Mechanic already assigned to this ticket"}), 400
    return jsonify({"error": "Invalid ticket-id or mechanic-id"}), 404

@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic_from_ticket(ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if service_ticket and mechanic:
        if mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify({"message": f"Successfully removed Mechanic {mechanic.name} from ticket {ticket_id}",
                            "tickets": service_ticket_schema.dump(service_ticket),
                            "mechanics": mechanics_schema.dump(service_ticket.mechanics)}), 200
        return jsonify({"error": "Mechanic not assigned to this ticket"}), 400
    return jsonify({"error": "Invalid ticket-id or mechanic-id"}), 404

@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    service_tickets = db.session.execute(query).scalars().all()
    
    if service_tickets:
        return service_tickets_schema.jsonify(service_tickets), 200
    return jsonify("message:" "no service tickets found"), 200
