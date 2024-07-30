from flask import jsonify

from app import oauth


def search():
    response = oauth.osu_auth.authorize_redirect()
    return jsonify({"authorization_url": response.headers["Location"]})
