from enum import Enum


class ServiceName(Enum):
    SCORE_FETCHER = "score_fetcher"
    MAPPER_INFO_FETCHER = "mapper_info_fetcher"


class QueueName(Enum):
    SCORE_FETCHER_TASKS = "score_fetcher_tasks"
    MAPPER_INFO_FETCHER_TASKS = "mapper_info_fetcher_tasks"


class EventName(Enum):
    SCORE_FETCHER_TASK_ADDED = "score_fetcher_task_added"
    MAPPER_INFO_FETCHER_TASK_ADDED = "mapper_info_fetcher_task_added"


class RuntimeTaskName(Enum):
    SCHEDULER_TASK = "scheduler_task"
    SUBSCRIBER_TASK = "subscriber_task"
