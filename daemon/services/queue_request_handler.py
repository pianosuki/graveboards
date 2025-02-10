import asyncio
import logging

from app.beatmap_manager import BeatmapManager
from app.database.schemas import RequestSchema
from app.redis import ChannelName, Namespace
from app.redis.models import QueueRequestHandlerTask
from app.utils import aware_utcnow
from .enums import EventName, RuntimeTaskName
from .service import Service

logger = logging.getLogger(__name__)


class QueueRequestHandler(Service):
    def __init__(self, *args):
        super().__init__(*args)

        self.pubsub = self.rc.pubsub()

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
                scheduled_task = asyncio.create_task(self.handle_queue_request(task))
                self.tasks[task.hashed_id] = scheduled_task
                scheduled_task.add_done_callback(self.handle_task_error)
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
            serialized_task = await self.rc.hgetall(task_hash_name)
            task = QueueRequestHandlerTask.deserialize(serialized_task)

            await self.task_queue.put(task)
            self.events[EventName.QUEUE_REQUEST_HANDLER_TASK_ADDED].set()

    @staticmethod
    def handle_task_error(task: asyncio.Task):
        try:
            task.result()
        except Exception as e:
            logger.error(f"Task '{task.get_name()}' failed with error: {e}", exc_info=True)

    async def handle_queue_request(self, task: QueueRequestHandlerTask):
        bm = BeatmapManager(self.db)
        await bm.archive(task.beatmapset_id)

        request_dict = RequestSchema.model_validate(task).model_dump(
            exclude={"user_profile", "queue"}
        )
        await self.db.add_request(**request_dict)

        task_hash_name = Namespace.QUEUE_REQUEST_HANDLER_TASK.hash_name(task.hashed_id)
        await self.rc.hset(task_hash_name, "completed_at", aware_utcnow().isoformat())
