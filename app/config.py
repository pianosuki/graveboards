import os

from dotenv import load_dotenv

load_dotenv()

CONNEXION_BASE_URL = "http://127.0.0.1:8000"

ANGULAR_BASE_URL = "http://127.0.0.1:4200"

FLASK_SERVER_ARGS = {
    "static_url_path": ""
}

OAUTH_AUTHORIZATION_CODE = {
    "name": "osu_auth",
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "authorize_url": "https://osu.ppy.sh/oauth/authorize",
    "authorize_params": None,
    "access_token_url": "https://osu.ppy.sh/oauth/token",
    "access_token_params": None,
    "refresh_token_url": None,
    "redirect_uri": os.path.join(ANGULAR_BASE_URL, "oauth/callback"),
    "client_kwargs": {"scope": "public identify"}
}

OAUTH_CLIENT_CREDENTIALS = {
    "name": "osu_client",
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "access_token_url": "https://osu.ppy.sh/oauth/token",
    "access_token_params": None,
    "refresh_token_url": None,
    "client_kwargs": {"scope": "public", "grant_type": "client_credentials"}
}

SPEC_DIR = os.path.abspath("api/v1")

OSU_USER_ID = os.getenv("OSU_USER_ID")

API_KEY = os.getenv("API_KEY")


class FlaskConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
