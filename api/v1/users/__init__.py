from app import db
from app.database.schemas import UserSchema, RoleSchema
from app.enums import RoleName
from app.security import authorization_required, matching_user_id_override


@authorization_required(RoleName.ADMIN)
def search(**kwargs):
    with db.session_scope() as session:
        users = db.get_users(session=session)
        users_data = UserSchema(many=True).dump(users)

    return users_data, 200


@authorization_required(RoleName.ADMIN, override=matching_user_id_override)
def get(user_id: int, **kwargs):
    with db.session_scope() as session:
        user = db.get_user(id=user_id, session=session)
        user_data = UserSchema().dump(user)

    return user_data, 200


@authorization_required(RoleName.ADMIN)
def post(body: dict, **kwargs):
    user_id = body["user_id"]

    if db.get_user(id=user_id):
        return {"message": f"The user with ID '{user_id}' already exists"}, 409

    with db.session_scope() as session:
        roles = RoleSchema(many=True, session=session).load(body["roles"]) if "roles" in body else []

    db.add_user(id=user_id, roles=roles)

    return {"message": "User added successfully!"}, 201
