import asyncio
import heapq
from datetime import datetime, timedelta, timezone

from api import v1 as api
from app import db, arc
from app.osu_api import OsuAPIClient, ScoreType
from app.database.models import ScoreFetcherTask
from app.redis import ChannelName
from app.utils import aware_utcnow
from .enums import EventName, RuntimeTaskName
from .service import Service

SCORE_FETCHER_INTERVAL_HOURS = 24


class ScoreFetcher(Service):
    def __init__(self):
        self.pubsub = arc.pubsub()
        self.oac = OsuAPIClient()

        self.runtime_tasks: dict[RuntimeTaskName, asyncio.Task] = {}
        self.tasks_heap: list[tuple[datetime, int]] = []

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

                db.update_score_fetcher_task(task_id, last_fetch=fetch_time)
            else:
                await self.events[EventName.SCORE_FETCHER_TASK_ADDED].wait()
                self.events[EventName.SCORE_FETCHER_TASK_ADDED].clear()

    async def task_subscriber(self):
        await self.pubsub.subscribe(ChannelName.SCORE_FETCHER_TASKS.value)

        async for message in self.pubsub.listen():
            if not message["type"] == "message" or not message["channel"].decode() == ChannelName.SCORE_FETCHER_TASKS.value:
                continue

            await asyncio.sleep(5)  # Wait until it's safe to assume the ScoreFetcherTask was fully committed

            task_id = int(message["data"].decode())
            task = db.get_score_fetcher_task(id=task_id)

            self.load_task(task)
            self.events[EventName.SCORE_FETCHER_TASK_ADDED].set()

    def preload_tasks(self):
        tasks = db.get_score_fetcher_tasks(enabled=True)

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
        task = db.get_score_fetcher_task(id=task_id)

        user_id = task.user_id
        scores = self.oac.get_user_scores(user_id, ScoreType.RECENT)

        for score in scores:
            if not self.score_is_submittable(score):
                continue

            api.scores.post(score)

    @staticmethod
    def score_is_submittable(score: dict) -> bool:
        beatmap_id = score["beatmap"]["id"]

        return bool(db.get_leaderboard(beatmap_id=beatmap_id))
