import asyncio
import heapq
from datetime import datetime, timedelta, timezone

from api import v1 as api
from app.osu_api import OsuAPIClient, ScoreType
from app.database.models import ScoreFetcherTask
from app.redis import ChannelName
from app.utils import aware_utcnow
from app.config import PRIMARY_ADMIN_USER_ID
from .enums import EventName, RuntimeTaskName
from .service import Service

SCORE_FETCHER_INTERVAL_HOURS = 24


class ScoreFetcher(Service):
    def __init__(self, *args):
        super().__init__(*args)

        self.pubsub = self.rc.pubsub()
        self.oac = OsuAPIClient()

        self.task_heap: list[tuple[datetime, int]] = []
        self.events: dict[EventName, asyncio.Event] = {event_name: asyncio.Event() for event_name in EventName.__members__.values()}

    async def run(self):
        await self.preload_tasks()
        self.runtime_tasks[RuntimeTaskName.SCHEDULER_TASK] = asyncio.create_task(self.task_scheduler(), name="Scheduler Task")
        self.runtime_tasks[RuntimeTaskName.SUBSCRIBER_TASK] = asyncio.create_task(self.task_subscriber(), name="Subscriber Task")
        await asyncio.gather(*self.runtime_tasks.values())

    async def task_scheduler(self):  # TODO: Fix async execution of tasks (currently gets stuck waiting for each delay)
        while True:
            if self.task_heap:
                execution_time, task_id = heapq.heappop(self.task_heap)
                delay = (execution_time - aware_utcnow()).total_seconds()

                if delay > 0:
                    await asyncio.sleep(delay)

                await self.fetch_scores(task_id)

                fetch_time = aware_utcnow()
                next_execution_time = fetch_time + timedelta(hours=SCORE_FETCHER_INTERVAL_HOURS)
                heapq.heappush(self.task_heap, (next_execution_time, task_id))

                await self.db.update_score_fetcher_task(task_id, last_fetch=fetch_time)
            else:
                await self.events[EventName.SCORE_FETCHER_TASK_ADDED].wait()
                self.events[EventName.SCORE_FETCHER_TASK_ADDED].clear()

    async def task_subscriber(self):
        await self.pubsub.subscribe(ChannelName.SCORE_FETCHER_TASKS.value)

        async for message in self.pubsub.listen():
            if not message["type"] == "message" or not message["channel"] == ChannelName.SCORE_FETCHER_TASKS.value:
                continue

            # Wait until it's safe to assume the ScoreFetcherTask was fully committed
            # TODO: This is not 100% reliable, need to find another approach
            await asyncio.sleep(5)

            task_id = int(message["data"])
            task = await self.db.get_score_fetcher_task(id=task_id)

            self.load_task(task)
            self.events[EventName.SCORE_FETCHER_TASK_ADDED].set()

    async def preload_tasks(self):
        tasks = await self.db.get_score_fetcher_tasks(enabled=True)

        for task in tasks:
            self.load_task(task)

    def load_task(self, task: ScoreFetcherTask):
        if not task.enabled:
            return

        if task.last_fetch is not None:
            execution_time = task.last_fetch.replace(tzinfo=timezone.utc) + timedelta(hours=SCORE_FETCHER_INTERVAL_HOURS)
        else:
            execution_time = aware_utcnow()

        heapq.heappush(self.task_heap, (execution_time, task.id))

    async def fetch_scores(self, task_id: int):
        task = await self.db.get_score_fetcher_task(id=task_id)

        if not task:
            raise ValueError(f"Task with ID '{task_id}' not found")

        scores = await self.oac.get_user_scores(task.user_id, ScoreType.RECENT)

        for score in scores:
            if not await self.score_is_submittable(score):
                continue

            await api.scores.post(score, user=PRIMARY_ADMIN_USER_ID)

    async def score_is_submittable(self, score: dict) -> bool:
        return bool(await self.db.get_leaderboard(beatmap_id=score["beatmap"]["id"]))
