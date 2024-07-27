from flask import abort

from app import cr, sync, oac
from app.models import Mapper
from app.schemas import mappers_schema
from app.services import ServiceName, QueueName


def search():
    mappers = Mapper.query.all()
    return mappers_schema.dump(mappers), 200


def post(body: dict):
    mapper_id = body["user_id"]

    if cr.get_mapper(id=mapper_id):
        abort(409, f"The mapper with ID '{mapper_id}' already exists")
    else:
        user_dict = oac.get_user(mapper_id)
        cr.add_mapper(user_dict)

    mapper_info_fetcher_task = cr.get_mapper_info_fetcher_task(mapper_id=mapper_id)

    if not mapper_info_fetcher_task:
        task = cr.add_mapper_info_fetcher_task(mapper_id)
        sync.daemon.services[ServiceName.MAPPER_INFO_FETCHER].queues[QueueName.MAPPER_INFO_FETCHER_TASKS].put(task.id)
