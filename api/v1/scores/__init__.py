from app import cr
from app.schemas import scores_schema


def search(**kwargs):
    # To-do: handle filtering
    scores = cr.get_scores()
    return scores_schema.dump(scores), 200
