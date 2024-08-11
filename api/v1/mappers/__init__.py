from app import db
from app.osu_api import OsuAPIClient
from app.database.schemas import MapperSchema


def search():
    with db.session_scope() as session:
        mappers = db.get_mappers(session=session)
        mappers_data = MapperSchema(many=True).dump(mappers)

    return mappers_data, 200


def post(body: dict):
    mapper_id = body["user_id"]

    if db.get_mapper(id=mapper_id):
        return {"message": f"The mapper with ID '{mapper_id}' already exists"}, 409
    else:
        oac = OsuAPIClient()

        user_dict = oac.get_user(mapper_id)

        with db.session_scope() as session:
            mapper = MapperSchema(session=session).load(user_dict)
            session.add(mapper)

    return {"message": "Mapper added successfully!"}, 201
