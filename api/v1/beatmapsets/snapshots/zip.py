from werkzeug.wrappers import Response

from app.beatmap_manager import BeatmapManager


def search(beatmapset_id: int, snapshot_number: int):
    bm = BeatmapManager()

    zip_file_io = bm.get_zip(beatmapset_id, snapshot_number)
    zip_file_io.seek(0)

    response = Response(
        zip_file_io,
        headers={"Content-Disposition": f"attachment; filename={beatmapset_id}.zip"},
        mimetype="application/zip"
    )

    return response
