from marshmallow import fields
from app import db, ma
from .models import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    osu_id = fields.String(required=False)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
