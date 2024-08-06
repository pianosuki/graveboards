from api import v1 as api
from app import flask_app, db, cr
from app.config import API_KEY, OSU_USER_ID, MASTER_QUEUE_NAME, MASTER_QUEUE_DESCRIPTION, ADMIN_ROLE_NAME, ADMIN_OSU_USER_IDS


def setup():
    with flask_app.app_context():
        db.create_all()

        if not cr.user_exists(OSU_USER_ID):
            cr.add_role(ADMIN_ROLE_NAME)
            print(f"Added role: '{ADMIN_ROLE_NAME}'")

            api.users.post({"user_id": OSU_USER_ID, "roles": [{"name": ADMIN_ROLE_NAME}]})
            print(f"Added primary admin: {OSU_USER_ID}")

            admin_user_ids = ADMIN_OSU_USER_IDS.copy()
            admin_user_ids.remove(OSU_USER_ID)

            for user_id in admin_user_ids:
                api.users.post({"user_id": user_id, "roles": [{"name": ADMIN_ROLE_NAME}]})

            print(f"Added admins: {admin_user_ids}")

            cr.add_api_key(API_KEY, OSU_USER_ID)
            print(f"Added API key")

            cr.add_queue(OSU_USER_ID, MASTER_QUEUE_NAME, description=MASTER_QUEUE_DESCRIPTION)
            print(f"Added master queue")

            # Add Net0's queue for now until we have an admin panel to do this manually
            cr.add_queue(5099768, "Net0's Queue", description="Net0's BN modding queue")
            print(f"Added Net0's queue")


if __name__ == "__main__":
    setup()
