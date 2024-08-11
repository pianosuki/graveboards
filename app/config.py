import os

from dotenv import load_dotenv

load_dotenv()

FRONTEND_BASE_URL = os.getenv("BASE_URL")
SPEC_DIR = os.path.abspath("api/v1")
INSTANCE_DIR = os.path.abspath("instance")

POSTGRESQL_CONFIGURATION = {
    "drivername": "postgresql+psycopg2",
    "host": os.getenv("POSTGRESQL_HOST"),
    "port": os.getenv("POSTGRESQL_PORT"),
    "username": os.getenv("POSTGRESQL_USERNAME"),
    "password": os.getenv("POSTGRESQL_PASSWORD"),
    "database": os.getenv("POSTGRESQL_DATABASE")
}

REDIS_CONFIGURATION = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
    "username": os.getenv("REDIS_USERNAME"),
    "password": os.getenv("REDIS_PASSWORD"),
    "db": os.getenv("REDIS_DB"),
    "ssl": os.getenv("REDIS_SSL")
}

OAUTH_CONFIGURATION = {
    "client_id": os.getenv("OSU_CLIENT_ID"),
    "client_secret": os.getenv("OSU_CLIENT_SECRET"),
    "redirect_uri": FRONTEND_BASE_URL + "/callback",
    "authorize_url": "https://osu.ppy.sh/oauth/authorize",
    "token_endpoint": "https://osu.ppy.sh/oauth/token",
    "token_endpoint_auth_method": "client_secret_basic"
}

ADMIN_ROLE_NAME = "admin"
ADMIN_USER_IDS = [int(id_.strip()) for id_ in os.getenv("ADMIN_USER_IDS").split(",")]
API_KEY = os.getenv("API_KEY")
MASTER_QUEUE_NAME = "Graveboards Queue"
MASTER_QUEUE_DESCRIPTION = "Master queue for beatmaps to receive leaderboards"
