from app import oauth


def search():
    return oauth.osu_auth.authorize_redirect()
