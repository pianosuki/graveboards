from app import db
from app.database.schemas import BeatmapsetListingSchema
from app.search import SearchEngine


def search(**kwargs):
    se = SearchEngine()

    try:
        results = se.search(**kwargs)
    except (ValueError, TypeError) as e:
        return {"message": str(e)}, 400

    with db.session_scope() as session:
        try:
            next(results)
            page = results.send(session)
        except StopIteration:
            return [], 200

        page_data = BeatmapsetListingSchema(many=True, session=session).dump(page)

    return page_data, 200
