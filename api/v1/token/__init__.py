from authlib.integrations.base_client.errors import OAuthError
from connexion import request

from app.database import PostgresqlDB
from app.database.schemas import JWTSchema
from app.oauth import OAuth
from app.osu_api import OsuAPIClient
from app.security import create_token_payload, encode_token


async def search(token: str):
    db: PostgresqlDB = request.state.db

    jwt = await db.get_jwt(token=token)

    if not jwt:
        return {"message": f"The JWT provided does not exist"}, 404

    jwt_data = JWTSchema.model_validate(jwt).model_dump()

    return jwt_data, 200


async def post(body: dict):
    db: PostgresqlDB = request.state.db

    try:
        oauth = OAuth()

        token = await oauth.fetch_token(grant_type="authorization_code", scope="public identify", code=body["code"])
        access_token = token["access_token"]
        refresh_token = token["refresh_token"]
        expires_at = token["expires_at"]

        oac = OsuAPIClient()

        user_data = await oac.get_own_data(access_token)
        user_id = user_data["id"]

        if not await db.get_user(id=user_id):
            await db.add_user(id=user_id)

        score_fetcher_task = await db.get_score_fetcher_task(user_id=user_id)

        if not score_fetcher_task.enabled and score_fetcher_task.last_fetch is None:
            await db.update_score_fetcher_task(score_fetcher_task.id, enabled=True)

        oauth_tokens = await db.get_oauth_tokens(user_id=user_id, is_revoked=False)

        for oauth_token in oauth_tokens:
            await db.update_oauth_token(oauth_token.id, is_revoked=True)  # TODO: Properly utilize refresh token

        await db.add_oauth_token(user_id=user_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)

        payload = create_token_payload(user_id)
        jwt_str = encode_token(payload)

        jwt = await db.add_jwt(user_id=user_id, token=jwt_str, issued_at=payload["iat"], expires_at=payload["exp"])
        jwt_data = JWTSchema.model_validate(jwt).model_dump()

        return jwt_data, 201
    except OAuthError as e:
        return {"message": e.description}, 500
