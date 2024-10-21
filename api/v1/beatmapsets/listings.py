from app import db
from app.database.schemas import BeatmapsetListingSchema
from app.search import SearchEngine


def search(**kwargs):
    with db.session_scope() as session:
        se = SearchEngine()

        results = se.search(**kwargs)

        next(results)

        try:
            page = results.send(session)
        except StopIteration:
            return [], 200

        page_data = BeatmapsetListingSchema(many=True, session=session).dump(page)

    return page_data, 200
