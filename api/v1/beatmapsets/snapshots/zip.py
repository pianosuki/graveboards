from flask import send_file

from app import bm


def search(beatmapset_id: int, snapshot_number: int):
    zip_file = bm.get_zip(beatmapset_id, snapshot_number)
    return send_file(zip_file, as_attachment=True, download_name=f"{beatmapset_id}.zip"), 200