import json
import asyncio
from datetime import datetime, timezone

from httpx import HTTPStatusError

from app.database import PostgresqlDB
from app.database.schemas import ProfileSchema
from app.beatmap_manager import BeatmapManager
from setup import setup


async def migrate():
    db = PostgresqlDB()

    print("Starting migration...\n")

    with open("requests.json", "r") as file:
        rows = json.load(file)
        total_rows = len(rows)

        for i, row in enumerate(rows, start=1):
            beatmapset_id = row["beatmapset_id"]
            row["created_at"] = datetime.fromisoformat(row["created_at"]).replace(tzinfo=timezone.utc)
            row["updated_at"] = datetime.fromisoformat(row["updated_at"]).replace(tzinfo=timezone.utc)

            if not await db.get_beatmapset(id=beatmapset_id):
                try:
                    bm = BeatmapManager(db)
                    await bm.archive(beatmapset_id)
                except HTTPStatusError as e:
                    if e.response.status_code == 404:
                        continue

            if not await db.get_request(**row):
                await db.add_request(**row)

            progress = int((i / total_rows) * 100)
            bar = "=" * (progress // 2)
            spaces = " " * (50 - len(bar))

            if __name__ == "__main__":
                print(f"\r[requests] [{bar}{spaces}] {progress}% ({i}/{total_rows})", end="")

    print("\nMigration complete!")


if __name__ == "__main__":
    asyncio.run(setup())
    asyncio.run(migrate())
