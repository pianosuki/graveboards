import httpx
from flask import request, abort
from app import bm


def search():
    pass


def get():
    pass


def post():
    beatmap_id = request.json["beatmap_id"]
    try:
        bm.download(beatmap_id)
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())
