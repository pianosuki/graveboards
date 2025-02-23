from enum import Enum


class ChannelName(Enum):
    SCORE_FETCHER_TASKS = "score_fetcher_tasks"
    PROFILE_FETCHER_TASKS = "profile_fetcher_tasks"
    QUEUE_REQUEST_HANDLER_TASKS = "queue_request_handler_tasks"


class Namespace(Enum):
    LOCK = "lock"
    OSU_CLIENT_OAUTH_TOKEN = "osu_client_oauth_token"
    OSU_USER_PROFILE = "osu_user_profile"
    CSRF_STATE = "csrf_state"
    QUEUE_REQUEST_HANDLER_TASK = "queue_request_handler_task"
    BEATMAPSET_CACHE = "beatmapset_cache"

    def hash_name(self, suffix: int | str) -> str:
        return f"{self.value}:{suffix}"
