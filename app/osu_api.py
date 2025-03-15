import time
import asyncio
from enum import Enum

import httpx
from pydantic import ValidationError

from .redis import RedisClient, Namespace, LOCK_EXPIRY, CACHED_BEATMAP_EXPIRY, CACHED_BEATMAPSET_EXPIRY, rate_limit
from .redis.models import OsuClientOAuthToken, Beatmapset, Beatmap
from .oauth import OAuth
from .logger import logger

API_BASEURL = "https://osu.ppy.sh/api/v2"
MAX_TOKEN_FETCH_RETRIES = 3
RATE_LIMIT = 60

class APIEndpoint(Enum):
    # Beatmaps
    BEATMAP_PACKS = API_BASEURL + "/beatmaps/packs"
    BEATMAP_LOOKUP = API_BASEURL + "/beatmaps/lookup"
    BEATMAP_USER_SCORE = API_BASEURL + "/beatmaps/{beatmap}/scores/users/{user}"
    BEATMAP_USER_SCORES = API_BASEURL + "/beatmaps/{beatmap}/scores/users/{user}/all"
    BEATMAP_SCORES = API_BASEURL + "/beatmaps/{beatmap}/scores"
    BEATMAPS = API_BASEURL + "/beatmaps"
    BEATMAP = API_BASEURL + "/beatmaps/{beatmap}"
    BEATMAP_ATTRIBUTES = API_BASEURL + "/beatmaps/{beatmap}/attributes"

    # Beatmapsets
    BEATMAPSET_LOOKUP = API_BASEURL + "/beatmapsets/lookup"
    BEATMAPSET = API_BASEURL + "/beatmapsets/{beatmapset}"

    # Users
    ME = API_BASEURL + "/me"
    SCORES = API_BASEURL + "/users/{user}/scores/{type}"
    USER = API_BASEURL + "/users/{user}/{mode}"

    def format(self, *args, **kwargs) -> str:
        args = [arg if arg is not None else "" for arg in args]
        kwargs = {key: value if value is not None else "" for key, value in kwargs.items()}

        return str.format(self.value, *args, **kwargs).rstrip("/")


class ScoreType(Enum):
    BEST = "best"
    FIRSTS = "firsts"
    RECENT = "recent"


class Ruleset(Enum):
    FRUITS = "fruits"
    MANIA = "mania"
    OSU = "osu"
    TAIKO = "taiko"


class OsuAPIClientBase:
    def __init__(self, rc: RedisClient):
        self.rc = rc
        self._oauth = OAuth()
        self._token: OsuClientOAuthToken | None = None

    async def get_token(self) -> str:
        async def get_valid_token_from_redis() -> OsuClientOAuthToken | None:
            serialized_token = await self.rc.hgetall(Namespace.OSU_CLIENT_OAUTH_TOKEN.value)

            if serialized_token:
                try:
                    token_ = OsuClientOAuthToken.deserialize(serialized_token)

                    if token_.expires_at > time.time():
                        return token_
                except (ValidationError, ValueError):
                    pass

            return None

        async def do_refresh_token():
            try:
                await self.refresh_token()
            finally:
                await self.rc.delete(lock_hash_name)

        if self._token and self._token.expires_at > time.time():
            return self._token.access_token

        if token := await get_valid_token_from_redis():
            self._token = token
            return token.access_token

        lock_hash_name = Namespace.LOCK.hash_name(Namespace.OSU_CLIENT_OAUTH_TOKEN.value)
        lock_acquired = await self.rc.set(lock_hash_name, "locked", ex=LOCK_EXPIRY, nx=True)

        if lock_acquired:
            await do_refresh_token()
        else:
            for _ in range(LOCK_EXPIRY):
                await asyncio.sleep(1)

                if token := await get_valid_token_from_redis():
                    self._token = token
                    return token.access_token

            await do_refresh_token()

        return self._token.access_token

    async def refresh_token(self):
        for attempt in range(MAX_TOKEN_FETCH_RETRIES):
            try:
                token_dict = await self._oauth.fetch_token(grant_type="client_credentials", scope="public")
                token = OsuClientOAuthToken.model_validate(token_dict)
                await self.rc.hset(Namespace.OSU_CLIENT_OAUTH_TOKEN.value, mapping=token.serialize())
                self._token = token
                return
            except httpx.ReadTimeout:
                if attempt < MAX_TOKEN_FETCH_RETRIES:
                    await asyncio.sleep(2 ** attempt)
                    continue

                raise TimeoutError(f"Failed to fetch token after {MAX_TOKEN_FETCH_RETRIES} retries due to ReadTimeout")

    async def get_auth_headers(self, access_token: str = None) -> dict:
        return {"Authorization": f"Bearer {access_token or await self.get_token()}"}

    @staticmethod
    def format_query_parameters(query_parameters: dict) -> str:
        parameter_strings = [f"{key}={value}" for key, value in query_parameters.items()]

        return f"?{'&'.join(parameter_strings)}"


class OsuAPIClient(OsuAPIClientBase):
    # BEATMAPS
    @rate_limit(RATE_LIMIT)
    async def get_beatmap(self, beatmap_id: int) -> dict:
        async def get_cached_beatmap_from_redis() -> Beatmap | None:
            if serialized_beatmap := await self.rc.hgetall(cached_beatmap_hash_name):
                try:
                    return Beatmap.deserialize(serialized_beatmap)
                except (ValidationError, ValueError) as e:
                    logger.warning(f"Error when deserializing from redis cache: {e}")

            return None

        cached_beatmap_hash_name = Namespace.CACHED_BEATMAP.hash_name(beatmap_id)

        if cached_beatmap := await get_cached_beatmap_from_redis():
            return cached_beatmap.model_dump(mode="json")

        url = APIEndpoint.BEATMAP.format(beatmap=beatmap_id)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **await self.get_auth_headers()
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()
        beatmap_data = response.json()

        cached_beatmap = Beatmapset.model_validate(beatmap_data)
        await self.rc.hset(cached_beatmap_hash_name, mapping=cached_beatmap.serialize())
        await self.rc.expire(cached_beatmap_hash_name, CACHED_BEATMAP_EXPIRY)

        return beatmap_data

    @rate_limit(RATE_LIMIT)
    async def get_beatmapset(self, beatmapset_id: int) -> dict:
        async def get_cached_beatmapset_from_redis() -> Beatmapset | None:
            if serialized_beatmapset := await self.rc.hgetall(cached_beatmapset_hash_name):
                try:
                    return Beatmapset.deserialize(serialized_beatmapset)
                except (ValidationError, ValueError) as e:
                    logger.warning(f"Error when deserializing from redis cache: {e}")

            return None

        cached_beatmapset_hash_name = Namespace.CACHED_BEATMAPSET.hash_name(beatmapset_id)

        if cached_beatmapset := await get_cached_beatmapset_from_redis():
            return cached_beatmapset.model_dump(mode="json")

        url = APIEndpoint.BEATMAPSET.format(beatmapset=beatmapset_id)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **await self.get_auth_headers()
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()
        beatmapset_data = response.json()

        cached_beatmapset = Beatmapset.model_validate(beatmapset_data)
        await self.rc.hset(cached_beatmapset_hash_name, mapping=cached_beatmapset.serialize())
        await self.rc.expire(cached_beatmapset_hash_name, CACHED_BEATMAPSET_EXPIRY)

        return beatmapset_data

    # USERS
    @rate_limit(RATE_LIMIT)
    async def get_own_data(self, access_token: str) -> dict:
        url = APIEndpoint.ME.value

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **await self.get_auth_headers(access_token)
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()
        return response.json()

    @rate_limit(RATE_LIMIT)
    async def get_user_scores(self, user_id: int, score_type: ScoreType, legacy_only: int = 0, include_fails: int = 0, mode: Ruleset | None = None, limit: int | None = None, offset: int | None = None):
        url = APIEndpoint.SCORES.format(user=user_id, type=score_type.value)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **await self.get_auth_headers()
        }

        query_parameters = {
            "legacy_only": legacy_only,
            "include_fails": include_fails,
        }

        if mode is not None:
            query_parameters["mode"] = mode.value

        if limit is not None:
            query_parameters["limit"] = limit

        if offset is not None:
            query_parameters["offset"] = offset

        url += self.format_query_parameters(query_parameters)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()
        return response.json()

    @rate_limit(RATE_LIMIT)
    async def get_user(self, user_id: int, mode: Ruleset | None = None) -> dict:
        url = APIEndpoint.USER.format(user=user_id, mode=mode)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **await self.get_auth_headers()
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()
        return response.json()
