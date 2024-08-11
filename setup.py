from app import db
from app.config import ADMIN_ROLE_NAME, ADMIN_USER_IDS, API_KEY, MASTER_QUEUE_NAME, MASTER_QUEUE_DESCRIPTION


def setup():
    db.create_database()

    if db.is_empty():
        with db.session_scope() as session:
            admin_role = db.add_role(name=ADMIN_ROLE_NAME, session=session)

            users = [db.add_user(id=admin_osu_user_id, roles=[admin_role], session=session) for admin_osu_user_id in ADMIN_USER_IDS]

            db.add_api_key(key=API_KEY, user_id=users[0].id, session=session)

            db.add_queue(user_id=users[0].id, name=MASTER_QUEUE_NAME, description=MASTER_QUEUE_DESCRIPTION, session=session)
            db.add_queue(user_id=5099768, name="Net0's BN Queue", description="Net0's BN modding queue", session=session)

            print(f"[{__name__}] Fresh database set up successfully!")


if __name__ == "__main__":
    setup()
