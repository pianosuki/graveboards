from flask import jsonify

from app import oac


def search(user_id: int):
    user_profile = oac.get_user(user_id)
    return jsonify(user_profile)
