import asyncio

from app import db, arc
from app.osu_api import OsuAPIClient
from app.beatmap_manager import BeatmapManager
from app.database.schemas import RequestSchema
from app.redis import ChannelName, Namespace
from app.redis.models import QueueRequestHandlerTask
from app.utils import aware_utcnow
from .enums import EventName, RuntimeTaskName
from .service import Service


class QueueRequestHandler(Service):
    def __init__(self):
        self.pubsub = arc.pubsub()
        self.oac = OsuAPIClient()

        self.runtime_tasks: dict[RuntimeTaskName, asyncio.Task] = {}
        self.task_queue: asyncio.Queue[QueueRequestHandlerTask] = asyncio.Queue()
        self.tasks: dict[int, asyncio.Task] = {}
        self.events: dict[EventName, asyncio.Event] = {event_name: asyncio.Event() for event_name in EventName.__members__.values()}

    async def run(self):
        self.runtime_tasks[RuntimeTaskName.SCHEDULER_TASK] = asyncio.create_task(self.task_scheduler(), name="Scheduler Task")
        self.runtime_tasks[RuntimeTaskName.SUBSCRIBER_TASK] = asyncio.create_task(self.task_subscriber(), name="Subscriber Task")
        await asyncio.gather(*self.runtime_tasks.values())

    async def task_scheduler(self):
        while True:
            if not self.task_queue.empty():
                task = await self.task_queue.get()
                self.tasks[task.hashed_id] = asyncio.create_task(self.handle_queue_request(task))
            else:
                await self.events[EventName.QUEUE_REQUEST_HANDLER_TASK_ADDED].wait()
                self.events[EventName.QUEUE_REQUEST_HANDLER_TASK_ADDED].clear()

    async def task_subscriber(self):
        await self.pubsub.subscribe(ChannelName.QUEUE_REQUEST_HANDLER_TASKS.value)

        async for message in self.pubsub.listen():
            if not message["type"] == "message" or not message["channel"] == ChannelName.QUEUE_REQUEST_HANDLER_TASKS.value:
                continue

            task_id = int(message["data"])
            task_hash_name = Namespace.QUEUE_REQUEST_HANDLER_TASK.hash_name(task_id)
            serialized_task = await arc.hgetall(task_hash_name)
            task = QueueRequestHandlerTask.deserialize(serialized_task)

            await self.task_queue.put(task)
            self.events[EventName.QUEUE_REQUEST_HANDLER_TASK_ADDED].set()

    async def handle_queue_request(self, task: QueueRequestHandlerTask):
        bm = BeatmapManager()
        bm.archive(task.beatmapset_id)

        request_dict = RequestSchema().dump(task.model_dump())
        db.add_request(**request_dict)

        task_hash_name = Namespace.QUEUE_REQUEST_HANDLER_TASK.hash_name(task.hashed_id)
        await arc.hset(task_hash_name, "completed_at", aware_utcnow().isoformat())
