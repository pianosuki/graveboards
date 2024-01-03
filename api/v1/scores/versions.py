from app import cr


def post(beatmap_id: int, version_number: int, body: dict):
    cr.add_score(body)
    print(f"Added score on leaderboard {beatmap_id}/{version_number}")
