from urllib.parse import urlparse, parse_qs

from flask import jsonify

from app import oauth


def search():
    response = oauth.osu_auth.authorize_redirect()
    authorization_url = response.headers["Location"]
    state = parse_qs(urlparse(authorization_url).query).get("state", [None])[0]

    return jsonify({
        "authorization_url": response.headers["Location"],
        "state": state
    })
