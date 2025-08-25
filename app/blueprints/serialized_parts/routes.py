from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import serialized_parts_bp
from .schemas import serialized_part_schema, responses_schema
from app.models import SerializedPart, db, PartDescription
from app.extensions import limiter


@serialized_parts_bp.route('/debug-session', methods=['GET'])
def debug_session():
    from flask import current_app
    print("Session:", db.session)
    return jsonify({
        "session": str(type(db.session)),
        "in_app_context": str(current_app is not None)
    })


@serialized_parts_bp.route('/', methods=['POST'])
@limiter.limit("15 per hour")
def create_serialized_part():
    payload = request.get_json() or {}
    loaded = serialized_part_schema.load(payload)

    
    if isinstance(loaded, SerializedPart):
        obj = loaded
    else:
        obj = SerializedPart(**loaded)

    db.session.add(obj)
    db.session.commit()

    
    return jsonify({
        "id": obj.id,
        "description": serialized_part_schema.dump(obj)
    }), 201

@serialized_parts_bp.route('/', methods=['GET'])
@limiter.exempt
def get_serialized_parts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(SerializedPart)
        serialized_parts = db.session.paginate(query, page=page, per_page=per_page)
        
        return responses_schema.jsonify(serialized_parts), 200 

    except:
        query = select(SerializedPart)
        serialized_parts = db.session.execute(query).scalars().all()

        if serialized_parts:
            return responses_schema.jsonify(serialized_parts), 200
        return jsonify({"message:" "no part descriptions found"}), 200

@serialized_parts_bp.route('/<int:id>', methods=['GET'])
def get_serialized_part(id):
    serialized_part = db.session.get(SerializedPart, id)

    if serialized_part:
        return jsonify({
            "brand": serialized_part.description.brand,
            "part": serialized_part.description.part,
            "part_id": serialized_part.id,
            "ticket_id": serialized_part.ticket_id,
        }), 200
    return jsonify({"error": "part description id not found"}), 404

@serialized_parts_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("5/hour")
def update_serialized_part(id):
    serialized_part = db.session.get(SerializedPart, id)

    if not serialized_part:
        return jsonify({"error": "Serialized part not found"}), 404

    try:
        payload = request.get_json() or {}
        serialized_part_schema.load(payload, instance=serialized_part, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400


    db.session.commit()
    return jsonify({"desc_id": serialized_part_schema.dump(serialized_part)}), 200

@serialized_parts_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_serialized_part(id):
    serialized_part = db.session.get(SerializedPart, id)

    if not serialized_part:
        return jsonify({"error": "part description id not found"}), 404

    db.session.delete(serialized_part)
    db.session.commit()
    return jsonify({"message": f"part description {id} deleted successfully"}), 200


@serialized_parts_bp.route("/stock/<int:desc_id>", methods=["GET"])
def get_individual_stock(desc_id):
    part_descriptions = db.session.get(PartDescription, desc_id)
    parts = part_descriptions.serialized_parts

    count = 0
    for part in parts:
        if not part.ticket_id:
            count += 1

    return jsonify({
        "Item": part_descriptions.brand and part_descriptions.part,
        "Quantity": count
        }), 200
    