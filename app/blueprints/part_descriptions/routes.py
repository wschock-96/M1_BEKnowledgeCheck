from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import part_descriptions_bp
from .schemas import part_description_schema, part_descriptions_schema
from app.models import PartDescription, db
from app.extensions import limiter, cache


@part_descriptions_bp.route('/', methods=['POST'])
@limiter.limit("15 per hour")
def create_part_description():
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_part_description = PartDescription(**part_description_data)

    db.session.add(new_part_description)
    db.session.commit()

    return part_description_schema.jsonify(new_part_description), 201

@part_descriptions_bp.route('/', methods=['GET'])
@cache.cached(timeout=30)
def get_part_descriptions():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(PartDescription)
        part_descriptions = db.session.paginate(query, page=page, per_page=per_page)
        
        return part_descriptions_schema.jsonify(part_descriptions), 200 

    except:
        query = select(PartDescription)
        part_descriptions = db.session.execute(query).scalars().all()

        if part_descriptions:
            return part_descriptions_schema.jsonify(part_descriptions), 200
        return jsonify({"message:" "no part descriptions found"}), 200

@part_descriptions_bp.route('/<int:id>', methods=['GET'])
def get_part_description(id):
    part_description = db.session.get(PartDescription, id)

    if part_description:
        return part_description_schema.jsonify(part_description), 200
    return jsonify({"error": "part description id not found"}), 404

@part_descriptions_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("15/hour")
def update_part_description(id):
    part_description = db.session.get(PartDescription, id)

    if not part_description:
        return jsonify({"error": "part description id not found"}), 404

    try:
        updated_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        setattr(part_description, key, value)

    db.session.commit()
    return part_description_schema.jsonify(part_description), 200

@part_descriptions_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_part_description(id):
    part_description = db.session.get(PartDescription, id)

    if not part_description:
        return jsonify({"error": "part description id not found"}), 404

    db.session.delete(part_description)
    db.session.commit()
    return jsonify({"message": f"part description {id} deleted successfully"}), 200

    