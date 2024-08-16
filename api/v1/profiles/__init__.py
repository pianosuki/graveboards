from app import db
from app.osu_api import OsuAPIClient
from app.database.schemas import ProfileSchema
from app.security import authorization_required
from app.enums import RoleName


def search():
    with db.session_scope() as session:
        profiles = db.get_profiles(session=session)
        profiles_data = ProfileSchema(many=True).dump(profiles)

    return profiles_data, 200


def get(user_id: int):
    with db.session_scope() as session:
        profile = db.get_profile(user_id=user_id, session=session)
        profile_data = ProfileSchema().dump(profile)

    return profile_data, 200


@authorization_required(RoleName.ADMIN)
def post(body: dict, **kwargs):
    user_id = body["user_id"]

    if db.get_profile(id=user_id):
        return {"message": f"The profile with user ID '{user_id}' already exists"}, 409
    else:
        oac = OsuAPIClient()

        user_dict = oac.get_user(user_id)

        with db.session_scope() as session:
            profile = ProfileSchema(session=session).load(user_dict)
            session.add(profile)

    return {"message": "Profile added successfully!"}, 201
