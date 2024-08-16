from authlib.integrations.base_client.errors import OAuthError

from api import v1 as api
from app import db
from app.oauth import OAuth
from app.osu_api import OsuAPIClient
from app.config import PRIMARY_ADMIN_USER_ID
from app.security import generate_token


def post(body: dict):
    try:
        oauth = OAuth()

        token = oauth.fetch_token(grant_type="authorization_code", scope="public identify", code=body["code"])
        access_token = token["access_token"]
        refresh_token = token["refresh_token"]
        expires_at = token["expires_at"]

        oac = OsuAPIClient()

        user_data = oac.get_own_data(access_token)
        user_id = user_data["id"]

        if not db.get_user(id=user_id):
            api.users.post({"user_id": user_id}, user=PRIMARY_ADMIN_USER_ID)

        score_fetcher_task = db.get_score_fetcher_task(user_id=user_id)

        if not score_fetcher_task.enabled and score_fetcher_task.last_fetch is None:
            db.update_score_fetcher_task(score_fetcher_task.id, enabled=True)

        oauth_tokens = db.get_oauth_tokens(user_id=user_id, is_revoked=False)

        for oauth_token in oauth_tokens:
            db.update_oauth_token(oauth_token.id, is_revoked=True)

        db.add_oauth_token(user_id=user_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)

        jwt = generate_token(user_id)

        return {"token": jwt, "user_id": user_id}, 201

    except OAuthError as e:
        return {"message": e.description}, 500
