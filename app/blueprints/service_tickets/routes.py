from . import service_tickets_bp
from app.models import ServiceTicket, Customer, Mechanic, db, SerializedPart, PartDescription
from flask import jsonify, request
from .schemas import service_ticket_schema, service_tickets_schema
from sqlalchemy import select
from marshmallow import ValidationError
from app.extensions import limiter
from app.blueprints.mechanics.schemas import mechanics_schema
from app.util.auth import admin_required
from app.blueprints.serialized_parts.schemas import serialized_parts_schema, responses_schema



@service_tickets_bp.route('/', methods=['POST'])
@limiter.limit("20 per hour", override_defaults=True)
@admin_required
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
@limiter.exempt
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
@limiter.exempt
def remove_mechanic_from_ticket(ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not service_ticket or not mechanic:
        return jsonify({"error": "Invalid ticket-id or mechanic-id"}), 404
    

    if mechanic not in service_ticket.mechanics:
            return jsonify({"message": f"Mechanic {mechanic.name} was not assigned to ticket {ticket_id}",
                            "tickets": service_ticket_schema.dump(service_ticket),
                            "mechanics": mechanics_schema.dump(service_ticket.mechanics)}), 200

    service_ticket.mechanics.remove(mechanic)
    db.session.commit()
            
    return jsonify({
        "message": f"Successfully removed Mechanic {mechanic.name} from ticket {ticket_id}",
        "tickets": service_ticket_schema.dump(service_ticket),
        "mechanics": mechanics_schema.dump(service_ticket.mechanics),
    }), 200    


@service_tickets_bp.route('/', methods=['GET'])
@limiter.exempt
def get_service_tickets():
    query = select(ServiceTicket)
    service_tickets = db.session.execute(query).scalars().all()
    
    if service_tickets:
        return service_tickets_schema.jsonify(service_tickets), 200
    return jsonify("message:" "no service tickets found"), 200


@service_tickets_bp.route('/<int:ticket_id>/add-part/<int:part_id>', methods=['PUT'])
@limiter.exempt
def add_part_to_ticket(ticket_id, part_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(SerializedPart, part_id)

    if not service_ticket or not part:
        return jsonify({"error": "Invalid ticket-id or part-id"}), 404
    

    if part.ticket_id == ticket_id:
        return jsonify({"message": f"{part.description.part} has aldready been assigned to ticket {ticket_id}",
                        "tickets": service_ticket_schema.dump(service_ticket),
                        "parts": serialized_parts_schema.dump(service_ticket.serialized_parts)}), 200
    
    if part.ticket_id and part.ticket_id != ticket_id:
        return jsonify({"error": "Part already assigned to another ticket"}), 400

    part.ticket = service_ticket
    db.session.commit()

    return jsonify({
        "message": f"Successfully added {part.description.part} to ticket {ticket_id}",
        "tickets": service_ticket_schema.dump(service_ticket),
        "parts": serialized_parts_schema.dump(service_ticket.serialized_parts),
    }), 200


@service_tickets_bp.route('/<int:ticket_id>/add-to-cart/<int:desc_id>', methods=['PUT'])
@limiter.exempt
def add_to_cart(ticket_id, desc_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    description = db.session.get(PartDescription, desc_id)

    parts = description.serialized_parts

    for part in parts:
        if not part.ticket_id:
            service_ticket.serialized_parts.append(part)
            db.session.commit()
            return jsonify({"message": f"Successfully added {part.description.part} to ticket {ticket_id}",
                            "tickets": service_ticket_schema.dump(service_ticket),
                            "parts": responses_schema.dump(service_ticket.serialized_parts)}), 200

    
    return jsonify({"error": "No available parts of this description to assign"}), 400