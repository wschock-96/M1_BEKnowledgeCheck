from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    tickets = fields.Method("get_ticket_ids")
    class Meta:
        model = Mechanic

    def get_ticket_ids(self, obj):
        return [ticket.id for ticket in obj.tickets]

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = MechanicSchema(exclude=('name', 'salary'))

