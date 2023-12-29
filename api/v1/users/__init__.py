from app.models import User
from app.schemas import users_schema


def search():
    users = User.query.all()
    return users_schema.dump(users), 200
