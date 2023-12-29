from flask import redirect, url_for, session, Blueprint
from authlib.integrations.flask_client import OAuthError
from app import oauth

oauth_bp = Blueprint("oauth", __name__)


@oauth_bp.route("/login")
def login():
    return oauth.osu_auth.authorize_redirect(url_for("oauth.authorized", _external=True))


@oauth_bp.route("/callback")
def authorized():
    try:
        token = oauth.osu_auth.authorize_access_token()
        session["oauth_token"] = token
    except OAuthError as e:
        print(f"OAuthError: {e}")
    finally:
        return redirect(url_for("main.index"))


@oauth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
