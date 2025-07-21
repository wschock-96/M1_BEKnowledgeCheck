from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import serialized_parts_bp
from .schemas import serialized_part_schema, serialized_parts_schema
from app.models import SerializedPart, db, PartDescription
from app.extensions import limiter, cache


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
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_serialized_part = SerializedPart(**serialized_part_data)

    db.session.add(new_serialized_part)
    db.session.commit()

    return jsonify({
        "message": f"Serialized part {new_serialized_part.description.brand} {new_serialized_part.description.part}: created successfully",
        "part": serialized_part_schema.dump(new_serialized_part)
    })

@serialized_parts_bp.route('/', methods=['GET'])
@limiter.exempt
def get_serialized_parts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(SerializedPart)
        serialized_parts = db.session.paginate(query, page=page, per_page=per_page)
        
        return serialized_parts_schema.jsonify(serialized_parts), 200 

    except:
        query = select(SerializedPart)
        serialized_parts = db.session.execute(query).scalars().all()

        if serialized_parts:
            return serialized_parts_schema.jsonify(serialized_parts), 200
        return jsonify({"message:" "no part descriptions found"}), 200

@serialized_parts_bp.route('/<int:id>', methods=['GET'])
def get_serialized_part(id):
    serialized_part = db.session.get(SerializedPart, id)

    if serialized_part:
        return serialized_part_schema.jsonify(serialized_part), 200
    return jsonify({"error": "part description id not found"}), 404

@serialized_parts_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("5/hour")
def update_serialized_part(id):
    serialized_part = db.session.get(SerializedPart, id)

    if not serialized_part:
        return jsonify({"error": "part description id not found"}), 404

    try:
        updated_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        setattr(serialized_part, key, value)

    db.session.commit()
    return serialized_part_schema.jsonify(serialized_part), 200

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
        "Item": part_descriptions.part,
        "Quantity": count
        }), 200
    