from connexion import request

from api.utils import pop_auth_info
from app.database import PostgresqlDB
from app.database.schemas import RequestListingSchema, BeatmapSnapshotSchema
from app.search import SearchEngine


async def search(**kwargs):  # TODO: Improve security
    db: PostgresqlDB = request.state.db

    pop_auth_info(kwargs)

    se = SearchEngine()

    async with db.session() as session:
        try:
            results_generator = se.search(session, requests_only=True, **kwargs)
        except (ValueError, TypeError) as e:
            return {"message": str(e)}, 400

        try:
            page = await anext(results_generator)
        except StopAsyncIteration:
            return [], 200

        context = {
            "exclusions": {
                BeatmapSnapshotSchema: {"beatmapset_snapshots", "leaderboard"}
            }
        }

        page_data = [
            RequestListingSchema.model_validate((beatmapset_listing.beatmapset_snapshot, request_)).model_dump(
                context=context
            )
            for beatmapset_listing, request_ in page
        ]

    return page_data, 200
