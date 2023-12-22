import os
from dotenv import load_dotenv

load_dotenv()

FLASK_SERVER_ARGS = {
    "static_url_path": os.path.abspath("/"),
    "static_folder": os.path.abspath("app/static"),
    "template_folder": os.path.abspath("app/templates")
}

OAUTH = {
    "name": "osu",
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "authorize_url": "https://osu.ppy.sh/oauth/authorize",
    "authorize_params": None,
    "access_token_url": "https://osu.ppy.sh/oauth/token",
    "access_token_params": None,
    "refresh_token_url": None,
    "redirect_uri": "http://localhost:8000/oauth/callback",
    "client_kwargs": {"scope": "public identify"}
}

SPEC_PATH = os.path.abspath("api/v1")

OSU_USER_ID = os.getenv("OSU_USER_ID")

API_KEY = os.getenv("API_KEY")


class FlaskConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
