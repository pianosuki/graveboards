from flask import send_file

from app import bm


def search(beatmap_id: int, snapshot_number: int):
    beatmap_path = bm.get_path(beatmap_id, snapshot_number)
    return send_file(beatmap_path, download_name=f"{beatmap_id}.osu"), 200
