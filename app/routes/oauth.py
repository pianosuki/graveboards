from flask import redirect, url_for, session, Blueprint
from authlib.integrations.flask_client import OAuthError

from api import v1 as api
from app import oauth, oac, cr

oauth_bp = Blueprint("oauth", __name__)


@oauth_bp.route("/login")
def login():
    return oauth.osu_auth.authorize_redirect(url_for("oauth.authorized", _external=True))


@oauth_bp.route("/callback")
def authorized():
    try:
        token = oauth.osu_auth.authorize_access_token()
        session["oauth_token"] = token
        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")
        expires_at = token.get("expires_at")

        user_data = oac.get_own_data(access_token)
        user_id = user_data.get("id")

        if not cr.user_exists(user_id):
            api.users.post({"user_id": user_id})

        oauth_tokens = cr.get_oauth_tokens(user_id=user_id, is_revoked=False)

        for oauth_token in oauth_tokens:
            cr.update_oauth_token(oauth_token.id, is_revoked=True)

        cr.add_oauth_token(user_id, access_token, refresh_token, expires_at)
    except OAuthError as e:
        print(f"OAuthError: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise e
    finally:
        return redirect(url_for("main.index"))


@oauth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
