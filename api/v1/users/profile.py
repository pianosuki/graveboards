from app.osu_api import OsuAPIClient


def search(user_id: int):
    oac = OsuAPIClient()
    user_profile = oac.get_user(user_id)

    return user_profile, 200
