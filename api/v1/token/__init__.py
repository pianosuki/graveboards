import json

from flask import abort
from authlib.integrations.flask_client import OAuthError

from api import v1 as api
from app import oauth, oac, cr


def post():
    try:
        token = oauth.osu_auth.authorize_access_token()
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

        return json.dumps(token), 201
    except OAuthError as e:
        print(f"OAuthError: {e}")
        abort(500, "Internal server error")
