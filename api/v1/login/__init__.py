from app.oauth import OAuth


def search():
    oauth = OAuth()

    authorization_url, state = oauth.create_authorization_url()

    return {
        "authorization_url": authorization_url,
        "state": state
    }, 200
