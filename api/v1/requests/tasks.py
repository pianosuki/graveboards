from app import rc
from app.security import role_authorization
from app.enums import RoleName
from app.redis import Namespace
from app.redis.models import QueueRequestHandlerTask


@role_authorization(RoleName.ADMIN)
def search(**kwargs):
    limit = kwargs.get("limit")
    offset = kwargs.get("offset")

    task_hash_names = rc.paginate_scan(f"{Namespace.QUEUE_REQUEST_HANDLER_TASK.value}:*", type_="HASH", limit=limit, offset=offset)
    serialized_tasks = [rc.hgetall(task_hash_name) for task_hash_name in task_hash_names]
    tasks = [QueueRequestHandlerTask.deserialize(serialized_task).model_dump(mode="json") for serialized_task in serialized_tasks]

    return tasks, 200


def get(task_id: int):
    task_hash_name = Namespace.QUEUE_REQUEST_HANDLER_TASK.hash_name(task_id)
    serialized_task = rc.hgetall(task_hash_name)

    if not serialized_task:
        return {"message": f"Request task with ID '{task_id}' not found"}, 404

    task = QueueRequestHandlerTask.deserialize(serialized_task).model_dump(mode="json")

    return task, 200
