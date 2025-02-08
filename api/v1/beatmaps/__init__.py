from connexion import request

from api.utils import prime_query_kwargs
from app.database import PostgresqlDB
from app.database.schemas import BeatmapSchema
from . import snapshots


async def search(**kwargs):
    db: PostgresqlDB = request.state.db

    prime_query_kwargs(kwargs)

    beatmaps = await db.get_beatmaps(
        _exclude_lazy=True,
        **kwargs
    )
    beatmaps_data = [
        BeatmapSchema.model_validate(beatmap).model_dump(
            exclude={"leaderboards", "snapshots"}
        )
        for beatmap in beatmaps
    ]

    return beatmaps_data, 200
