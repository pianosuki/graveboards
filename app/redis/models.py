from typing import Optional, Any
from datetime import datetime
from ast import literal_eval

from pydantic import BaseModel, computed_field

__all__ = [
    "OsuClientOAuthToken",
    "QueueRequestHandlerTask",
    "Beatmap",
    "Beatmapset"
]


class OsuClientOAuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    expires_at: int

    def serialize(self) -> dict[str, str]:
        serialized_dict = {}

        for key, value in self.__dict__.items():
            serialized_dict[key] = str(value)

        return serialized_dict

    @classmethod
    def deserialize(cls, serialized_dict: dict[str, str]) -> "OsuClientOAuthToken":
        deserialized_dict = {}

        for key, value in serialized_dict.items():
            match key:
                case "expires_in" | "expires_at":
                    value = int(value)

            deserialized_dict[key] = value

        return cls.model_validate(deserialized_dict)


class QueueRequestHandlerTask(BaseModel):
    user_id: int
    beatmapset_id: int
    queue_id: int
    comment: str
    mv_checked: bool
    completed_at: datetime | None = None
    failed_at: datetime | None = None

    @computed_field
    @property
    def hashed_id(self) -> int:
        return hash((self.queue_id, self.beatmapset_id)) & 0x7FFFFFFFFFFFFFFF

    def serialize(self) -> dict[str, str]:
        serialized_dict = {}

        for key, value in self.__dict__.items():
            match key:
                case "completed_at" | "failed_at":
                    value = value.isoformat() if value is not None else ""

            serialized_dict[key] = str(value)

        return serialized_dict

    @classmethod
    def deserialize(cls, serialized_dict: dict[str, str]) -> "QueueRequestHandlerTask":
        deserialized_dict = {}

        for key, value in serialized_dict.items():
            match key:
                case "user_id" | "beatmapset_id" | "queue_id":
                    value = int(value)
                case "mv_checked":
                    value = literal_eval(value)
                case "completed_at" | "failed_at":
                    value = datetime.fromisoformat(value) if value else None

            deserialized_dict[key] = value

        return cls.model_validate(deserialized_dict)


class Beatmap(BaseModel):
    id: int
    user_id: int
    accuracy: float
    ar: float
    bpm: float
    checksum: str
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    deleted_at: Optional[datetime]
    difficulty_rating: float
    drain: float
    failtimes: dict[str, Optional[list[int]]]
    hit_length: int
    last_updated: datetime
    max_combo: int
    mode: str
    mode_int: int
    owners: list[dict[str, str | int]]
    passcount: int
    playcount: int
    ranked: int
    status: str
    total_length: int
    url: str
    version: str

    def serialize(self) -> dict[str, str]:
        serialized_dict = {}

        for key, value in self.__dict__.items():
            match key:
                case "deleted_at" | "last_updated":
                    value = value.isoformat() if value is not None else ""

            serialized_dict[key] = str(value) if value is not None else ""

        return serialized_dict

    @classmethod
    def deserialize(cls, serialized_dict: dict[str, str]) -> "Beatmap":
        deserialized_dict = {}

        for key, value in serialized_dict.items():
            match key:
                case "id" | "beatmap_id" | "user_id" | "snapshot_number" | "count_circles" | "count_sliders" | "count_spinners" | "hit_length" | "max_combo" | "mode_int" | "passcount" | "playcount" | "ranked" | "total_length":
                    value = int(value)
                case "accuracy" | "ar" | "bpm" | "cs" | "difficulty_rating" | "drain":
                    value = float(value)
                case "failtimes" | "owners":
                    value = literal_eval(value)
                case "deleted_at" | "last_updated":
                    value = datetime.fromisoformat(value) if value else None

            deserialized_dict[key] = value

        return cls.model_validate(deserialized_dict)


class Beatmapset(BaseModel):
    id: int
    user_id: int
    artist: str
    artist_unicode: str
    availability: dict[str, bool | Optional[str]]
    covers: Optional[dict[str, str]]
    creator: str
    deleted_at: Optional[datetime]
    favourite_count: int
    genre: Optional[dict[str, int | str]]
    hype: Optional[dict[str, int]]
    language: Optional[dict[str, int | str]]
    last_updated: datetime
    nsfw: bool
    offset: int
    play_count: int
    preview_url: str
    ranked: int
    source: str
    status: str
    submitted_date: Optional[datetime]
    tags: str
    title: str
    title_unicode: str
    track_id: Optional[int]
    user: dict[str, Any]
    video: bool
    beatmaps: list["Beatmap"]

    def serialize(self) -> dict[str, str]:
        serialized_dict = {}

        for key, value in self.__dict__.items():
            match key:
                case "beatmaps":
                    value = [beatmap_cache.serialize() for beatmap_cache in value]

            serialized_dict[key] = str(value) if value is not None else ""

        return serialized_dict

    @classmethod
    def deserialize(cls, serialized_dict: dict[str, str]) -> "Beatmapset":
        deserialized_dict = {}

        for key, value in serialized_dict.items():
            match key:
                case "id" | "user_id" | "snapshot_number" | "favourite_count" | "offset" | "play_count" | "ranked" | "track_id":
                    value = int(value) if value else None
                case "verified" | "nsfw" | "video":
                    value = literal_eval(value.capitalize())
                case "availability" | "covers" | "genre" | "hype" | "language" | "user":
                    value = literal_eval(value) if value else None
                case "deleted_at" | "last_updated" | "submitted_date":
                    value = datetime.fromisoformat(value) if value else None
                case "beatmaps":
                    value = [Beatmap.deserialize(beatmap_cache) for beatmap_cache in literal_eval(value)]

            deserialized_dict[key] = value

        return cls.model_validate(deserialized_dict)
