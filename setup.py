from app import flask_app, db, cr
from app.config import API_KEY, OSU_USER_ID, MASTER_QUEUE_NAME, MASTER_QUEUE_DESCRIPTION


def setup():
    with flask_app.app_context():
        db.create_all()

        if not cr.user_exists(OSU_USER_ID):
            cr.add_user(OSU_USER_ID)
            print(f"Added admin: {OSU_USER_ID}")

            cr.add_api_key(API_KEY, OSU_USER_ID)
            print(f"Added API key for admin: {OSU_USER_ID}")

            cr.add_score_fetcher_task(OSU_USER_ID)
            print(f"Added score fetcher task for admin: {OSU_USER_ID}")

            cr.add_queue(OSU_USER_ID, MASTER_QUEUE_NAME, description=MASTER_QUEUE_DESCRIPTION)
            print(f"Added queue for admin: {OSU_USER_ID}")

            cr.add_queue(5099768, "Net0's Queue", description="Net0's BN modding queue")
            print(f"Added Net0's queue")


if __name__ == "__main__":
    setup()
