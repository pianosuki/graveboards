from io import BytesIO

from starlette.responses import PlainTextResponse

from app import db
from app.beatmap_manager import BeatmapManager


def search(beatmap_id: int, snapshot_number: int):
    if not db.get_beatmap_snapshot(beatmap_id=beatmap_id, snapshot_number=snapshot_number):
        return {"message": f"There is no beatmap snapshot with beatmap ID '{beatmap_id}' and snapshot number '{snapshot_number}'"}, 404

    bm = BeatmapManager()
    dotosu_file_path = bm.get_path(beatmap_id, snapshot_number)

    with open(dotosu_file_path, 'rb') as file:
        dotosu_file_io = BytesIO(file.read())

    dotosu_file_io.seek(0)

    response = PlainTextResponse(
        content=dotosu_file_io.read().decode(),
        headers={"Content-Disposition": f"attachment; filename={beatmap_id}.osu"}
    )

    return response
