from app import connexion_app, db, cr
from config import API_KEY, OSU_USER_ID


def setup():
    with connexion_app.app.app_context():
        db.create_all()

        if not cr.user_exists(OSU_USER_ID):
            cr.add_user(OSU_USER_ID)
            print(f"Added admin: {OSU_USER_ID}")

            cr.add_api_key(API_KEY, OSU_USER_ID)
            print(f"Added API key for admin: {OSU_USER_ID}")
