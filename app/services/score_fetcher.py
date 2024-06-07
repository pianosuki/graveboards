import asyncio
import heapq
import queue
from datetime import datetime, timedelta, timezone
from enum import Enum

from flask import Flask

from api import v1 as api
from app import flask_app, cr, oac
from app.osu_api import ScoreType
from app.utils import aware_utcnow
from app.models import ScoreFetcherTask
from .service import Service

SCORE_FETCHER_INTERVAL_HOURS = 24


class QueueName(Enum):
    SCORE_FETCHER_TASKS = "score_fetcher_tasks"


class EventName(Enum):
    SCORE_FETCHER_TASK_ADDED = "score_fetcher_task_added"


class RuntimeTaskName(Enum):
    SCHEDULER_TASK = "scheduler_task"
    SUBSCRIBER_TASK = "subscriber_task"


class ScoreFetcher(Service):
    def __init__(self, app: Flask):
        super().__init__(app)

        self.runtime_tasks: dict[RuntimeTaskName, asyncio.Task] = {}
        self.tasks_heap: list[tuple[datetime, int]] = []

        self.queues: dict[QueueName, queue.Queue] = {queue_name: queue.Queue() for queue_name in QueueName.__members__.values()}
        self.events: dict[EventName, asyncio.Event] = {event_name: asyncio.Event() for event_name in EventName.__members__.values()}

    async def run(self):
        self.preload_tasks()
        self.runtime_tasks[RuntimeTaskName.SCHEDULER_TASK] = asyncio.create_task(self.task_scheduler(), name="Scheduler Task")
        self.runtime_tasks[RuntimeTaskName.SUBSCRIBER_TASK] = asyncio.create_task(self.task_subscriber(), name="Subscriber Task")
        await asyncio.gather(*self.runtime_tasks.values())

    async def task_scheduler(self):
        while True:
            if self.tasks_heap:
                execution_time, task_id = heapq.heappop(self.tasks_heap)
                delay = (execution_time - aware_utcnow()).total_seconds()

                if delay > 0:
                    await asyncio.sleep(delay)

                self.fetch_scores(task_id)

                fetch_time = aware_utcnow()
                next_execution_time = fetch_time + timedelta(hours=SCORE_FETCHER_INTERVAL_HOURS)
                heapq.heappush(self.tasks_heap, (next_execution_time, task_id))

                with flask_app.app_context():
                    cr.update_score_fetcher_task(task_id, last_fetch=fetch_time)
            else:
                await self.events[EventName.SCORE_FETCHER_TASK_ADDED].wait()
                self.events[EventName.SCORE_FETCHER_TASK_ADDED].clear()

    async def task_subscriber(self):
        while True:
            if self.queues[QueueName.SCORE_FETCHER_TASKS].qsize() > 0:
                task_id = self.queues[QueueName.SCORE_FETCHER_TASKS].get_nowait()

                with flask_app.app_context():
                    task = cr.get_score_fetcher_task(id=task_id)

                self.load_task(task)
                self.events[EventName.SCORE_FETCHER_TASK_ADDED].set()

            await asyncio.sleep(5)

    def preload_tasks(self):
        with flask_app.app_context():
            tasks = cr.get_score_fetcher_tasks()

        for task in tasks:
            self.load_task(task)

    def load_task(self, task: ScoreFetcherTask):
        if not task.enabled:
            return

        if task.last_fetch is not None:
            execution_time = task.last_fetch.replace(tzinfo=timezone.utc) + timedelta(hours=SCORE_FETCHER_INTERVAL_HOURS)
        else:
            execution_time = aware_utcnow()

        heapq.heappush(self.tasks_heap, (execution_time, task.id))

    def fetch_scores(self, task_id: int):
        with flask_app.app_context():
            task = cr.get_score_fetcher_task(id=task_id)

        user_id = task.user_id
        scores = oac.get_user_scores(user_id, ScoreType.RECENT)

        for score in scores:
            if not self.score_is_submittable(score):
                continue

            with flask_app.app_context():
                api.scores.post(score)

    @staticmethod
    def score_is_submittable(score: dict) -> bool:
        beatmap_id = score["beatmap"]["id"]

        with flask_app.app_context():
            leaderboards = cr.get_leaderboards(beatmap_id=beatmap_id)

        return bool(leaderboards)
