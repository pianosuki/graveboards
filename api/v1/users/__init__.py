from app import db
from app.database.schemas import UserSchema, RoleSchema


def search():
    with db.session_scope() as session:
        users = db.get_users(session=session)
        users_data = UserSchema(many=True).dump(users)

    return users_data, 200


def get(user_id: int):
    with db.session_scope() as session:
        user = db.get_user(id=user_id, session=session)
        user_data = UserSchema().dump(user)

    return user_data, 200


def post(body: dict):
    user_id = body["user_id"]

    if db.get_user(id=user_id):
        return {"message": f"The user with ID '{user_id}' already exists"}, 409

    with db.session_scope() as session:
        roles = RoleSchema(many=True, session=session).load(body["roles"]) if "roles" in body else []

    db.add_user(id=user_id, roles=roles)

    return {"message": "User added successfully!"}, 201
