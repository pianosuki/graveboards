from app import db
from app.security.api_key import generate_api_key
from app.enums import RoleName
from app.config import ADMIN_USER_IDS, MASTER_QUEUE_NAME, MASTER_QUEUE_DESCRIPTION


def setup():
    db.create_database()

    if db.is_empty():
        with db.session_scope() as session:
            admin_role = db.add_role(name=RoleName.ADMIN.value, session=session)

            for user_id in ADMIN_USER_IDS:
                db.add_user(id=user_id, roles=[admin_role], session=session)
                db.add_api_key(key=generate_api_key(), user_id=user_id, session=session)

            db.add_queue(user_id=ADMIN_USER_IDS[0], name=MASTER_QUEUE_NAME, description=MASTER_QUEUE_DESCRIPTION, session=session)
            db.add_queue(user_id=5099768, name="Net0's BN Queue", description="Net0's BN modding queue", session=session)

            print(f"[{__name__}] Fresh database set up successfully!")


if __name__ == "__main__":
    setup()
