import asyncio
import heapq
from datetime import datetime, timedelta, timezone

from app.osu_api import OsuAPIClient
from app.database.models import ProfileFetcherTask
from app.database.schemas import ProfileSchema
from app.redis import ChannelName
from app.utils import aware_utcnow
from .enums import EventName, RuntimeTaskName
from .service import Service

PROFILE_FETCHER_INTERVAL_HOURS = 24


class ProfileFetcher(Service):
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

    async def task_scheduler(self):
        while True:
            if self.task_heap:
                execution_time, task_id = heapq.heappop(self.task_heap)
                delay = (execution_time - aware_utcnow()).total_seconds()

                if delay > 0:
                    await asyncio.sleep(delay)

                await self.fetch_profile(task_id)

                fetch_time = aware_utcnow()
                next_execution_time = fetch_time + timedelta(hours=PROFILE_FETCHER_INTERVAL_HOURS)
                heapq.heappush(self.task_heap, (next_execution_time, task_id))

                await self.db.update_profile_fetcher_task(task_id, last_fetch=fetch_time)
            else:
                await self.events[EventName.PROFILE_FETCHER_TASK_ADDED].wait()
                self.events[EventName.PROFILE_FETCHER_TASK_ADDED].clear()

    async def task_subscriber(self):
        await self.pubsub.subscribe(ChannelName.PROFILE_FETCHER_TASKS.value)

        async for message in self.pubsub.listen():
            if not message["type"] == "message" or not message["channel"] == ChannelName.PROFILE_FETCHER_TASKS.value:
                continue

            await asyncio.sleep(5)  # Wait until it's safe to assume the MapperInfoFetcherTask was fully committed

            task_id = int(message["data"])
            task = await self.db.get_profile_fetcher_task(id=task_id)

            self.load_task(task)
            self.events[EventName.PROFILE_FETCHER_TASK_ADDED].set()

    async def preload_tasks(self):
        tasks = await self.db.get_profile_fetcher_tasks(enabled=True)

        for task in tasks:
            self.load_task(task)

    def load_task(self, task: ProfileFetcherTask):
        if not task.enabled:
            return

        if task.last_fetch is not None:
            execution_time = task.last_fetch.replace(tzinfo=timezone.utc) + timedelta(hours=PROFILE_FETCHER_INTERVAL_HOURS)
        else:
            execution_time = aware_utcnow()

        heapq.heappush(self.task_heap, (execution_time, task.id))

    async def fetch_profile(self, task_id: int):
        async with self.db.session() as session:
            task = await self.db.get_profile_fetcher_task(id=task_id, session=session)

            if not task:
                raise ValueError(f"Task with ID '{task_id}' not found")

            user_dict = await self.oac.get_user(task.user_id)

            profile = await self.db.get_profile(user_id=task.user_id, session=session)
            profile_dict = ProfileSchema.model_validate(user_dict).model_dump(
                exclude={"id", "updated_at", "is_restricted"}
            )

            if not profile:
                await self.db.add_profile(session=session, **profile_dict)
            else:
                await self.db.update_profile(profile.id, session=session, **profile_dict)
