from app.extensions import ma
from app.models import PartDescription, SerializedPart

class PartDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescription

part_description_schema = PartDescriptionSchema()
part_descriptions_schema = PartDescriptionSchema(many=True)

class SerializedPartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SerializedPart
        load_instance = True
        include_fk = True

class SerializedPartWithDescriptionSchema(SerializedPartSchema):
    description = ma.Nested(PartDescriptionSchema)

serialized_part_schema = SerializedPartSchema()
serialized_parts_schema = SerializedPartSchema(many=True)
response_schema = SerializedPartWithDescriptionSchema()
responses_schema = SerializedPartWithDescriptionSchema(many=True)