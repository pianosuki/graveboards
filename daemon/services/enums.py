from enum import Enum


class EventName(Enum):
    SCORE_FETCHER_TASK_ADDED = "score_fetcher_task_added"
    MAPPER_INFO_FETCHER_TASK_ADDED = "mapper_info_fetcher_task_added"


class RuntimeTaskName(Enum):
    SCHEDULER_TASK = "scheduler_task"
    SUBSCRIBER_TASK = "subscriber_task"
