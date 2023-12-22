from app import connexion_app, db
from app.models import ApiKey, User
from config import API_KEY, OSU_USER_ID


def setup():
    with connexion_app.app.app_context():
        db.create_all()

        admin = User.query.filter_by(osu_id=OSU_USER_ID).first()
        if admin is None:
            user = User(osu_id=OSU_USER_ID)
            db.session.add(user)
            db.session.commit()
            print(f"Added user: (id={user.id}, osu_id={OSU_USER_ID})")

            admin_key = ApiKey(key=API_KEY, user_id=user.id)
            db.session.add(admin_key)
            db.session.commit()
            print(f"Added API key for user {user.id}")
