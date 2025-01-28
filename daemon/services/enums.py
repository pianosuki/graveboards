from enum import Enum


class EventName(Enum):
    SCORE_FETCHER_TASK_ADDED = "score_fetcher_task_added"
    PROFILE_FETCHER_TASK_ADDED = "profile_fetcher_task_added"
    QUEUE_REQUEST_HANDLER_TASK_ADDED = "queue_request_handler_task_added"


class RuntimeTaskName(Enum):
    SCHEDULER_TASK = "scheduler_task"
    SUBSCRIBER_TASK = "subscriber_task"
