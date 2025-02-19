import asyncio
import heapq
import logging
from datetime import datetime, timedelta, timezone

from api import v1 as api
from app.osu_api import OsuAPIClient, ScoreType
from app.database.models import ScoreFetcherTask
from app.redis import ChannelName
from app.utils import aware_utcnow
from app.config import PRIMARY_ADMIN_USER_ID
from .enums import RuntimeTaskName
from .service import Service

logger = logging.getLogger(__name__)

SCORE_FETCHER_INTERVAL_HOURS = 24
PENDING_TASK_TIMEOUT_SECONDS = 60


class ScoreFetcher(Service):
    def __init__(self, *args):
        super().__init__(*args)

        self.pubsub = self.rc.pubsub()
        self.oac = OsuAPIClient()

        self.task_heap: list[tuple[datetime, int]] = []
        self.tasks: dict[int, asyncio.Task] = {}
        self.task_condition = asyncio.Condition()

    async def run(self):
        await self.preload_tasks()
        self.runtime_tasks[RuntimeTaskName.SCHEDULER_TASK] = asyncio.create_task(self.task_scheduler(), name="Scheduler Task")
        self.runtime_tasks[RuntimeTaskName.SUBSCRIBER_TASK] = asyncio.create_task(self.task_subscriber(), name="Subscriber Task")
        await asyncio.gather(*self.runtime_tasks.values())

    async def task_scheduler(self):
        while True:
            async with self.task_condition:
                while not self.task_heap:
                    await self.task_condition.wait()

                execution_time, task_id = heapq.heappop(self.task_heap)

            scheduled_task = asyncio.create_task(self.handle_task(execution_time, task_id))
            self.tasks[task_id] = scheduled_task
            scheduled_task.add_done_callback(self.handle_task_error)

    async def task_subscriber(self):
        await self.pubsub.subscribe(ChannelName.SCORE_FETCHER_TASKS.value)

        async for message in self.pubsub.listen():
            if not message["type"] == "message" or not message["channel"] == ChannelName.SCORE_FETCHER_TASKS.value:
                continue

            task_id = int(message["data"])

            try:
                task = await self.get_pending_task(task_id)
            except TimeoutError:
                logger.warning(f"Task {task_id} was not found in the database after waiting")
                continue

            async with self.task_condition:
                self.load_task(task)
                self.task_condition.notify()

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

    async def get_pending_task(self, task_id: int, timeout: int = PENDING_TASK_TIMEOUT_SECONDS) -> ScoreFetcherTask:
        start_time = aware_utcnow()

        while (aware_utcnow() - start_time).total_seconds() < timeout:
            task = await self.db.get_score_fetcher_task(id=task_id)

            if task:
                return task

            await asyncio.sleep(0.5)

        raise TimeoutError

    async def handle_task(self, execution_time: datetime, task_id: int):
        delay = (execution_time - aware_utcnow()).total_seconds()

        if delay > 0:
            await asyncio.sleep(delay)

        await self.fetch_scores(task_id)
        fetch_time = aware_utcnow()
        next_execution_time = fetch_time + timedelta(hours=SCORE_FETCHER_INTERVAL_HOURS)
        await self.db.update_profile_fetcher_task(task_id, last_fetch=fetch_time)

        async with self.task_condition:
            heapq.heappush(self.task_heap, (next_execution_time, task_id))
            self.task_condition.notify()

    @staticmethod
    def handle_task_error(task: asyncio.Task):
        try:
            task.result()
        except Exception as e:
            logger.error(f"Task '{task.get_name()}' failed with error: {e}", exc_info=True)

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
