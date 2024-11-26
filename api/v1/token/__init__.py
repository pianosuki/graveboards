from authlib.integrations.base_client.errors import OAuthError

from api import v1 as api
from app import db
from app.oauth import OAuth
from app.osu_api import OsuAPIClient
from app.config import PRIMARY_ADMIN_USER_ID
from app.security.jwt import create_payload, encode_token
from app.database.schemas import JWTSchema


def search(token: str):
    with db.session_scope() as session:
        jwt = db.get_jwt(token=token, session=session)

        if not jwt:
            return {"message": f"The JWT provided does not exist"}, 404

        jwt_data = JWTSchema(session=session).dump(jwt)

    return jwt_data, 200


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

        payload = create_payload(user_id)
        jwt_str = encode_token(payload)
        db.add_jwt(user_id=user_id, token=jwt_str, issued_at=payload["iat"], expires_at=payload["exp"])

        return {"token": jwt_str, "user_id": user_id}, 201

    except OAuthError as e:
        return {"message": e.description}, 500
