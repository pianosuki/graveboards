from starlette.responses import StreamingResponse

from app.beatmap_manager import BeatmapManager
from app.utils import stream_file


def search(beatmapset_id: int, snapshot_number: int):
    bm = BeatmapManager()

    zip_file_io = bm.get_zip(beatmapset_id, snapshot_number)

    response = StreamingResponse(
        content=stream_file(zip_file_io),
        headers={"Content-Disposition": f"attachment; filename={beatmapset_id}.zip"},
        media_type="application/zip"
    )

    return response
