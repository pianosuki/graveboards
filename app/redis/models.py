from datetime import datetime
from ast import literal_eval

from pydantic import BaseModel, computed_field

__all__ = [
    "OsuClientOAuthToken",
    "QueueRequestHandlerTask",
    "BeatmapCache",
    "BeatmapsetCache"
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


class BeatmapCache(BaseModel):
    id: int
    beatmapset_id: int
    user_id: int

    def serialize(self) -> dict[str, str]:
        serialized_dict = {}

        for key, value in self.__dict__.items():
            serialized_dict[key] = str(value)

        return serialized_dict

    @classmethod
    def deserialize(cls, serialized_dict: dict[str, str]) -> "BeatmapCache":
        deserialized_dict = {}

        for key, value in serialized_dict.items():
            match key:
                case "id" | "beatmapset_id" | "user_id":
                    value = int(value)

            deserialized_dict[key] = value

        return cls.model_validate(deserialized_dict)


class BeatmapsetCache(BaseModel):
    id: int
    user_id: int
    beatmaps: list["BeatmapCache"]

    def serialize(self) -> dict[str, str]:
        serialized_dict = {}

        for key, value in self.__dict__.items():
            match key:
                case "beatmaps":
                    value = [beatmap_cache.serialize() for beatmap_cache in value]

            serialized_dict[key] = str(value)

        return serialized_dict

    @classmethod
    def deserialize(cls, serialized_dict: dict[str, str]) -> "BeatmapsetCache":
        deserialized_dict = {}

        for key, value in serialized_dict.items():
            match key:
                case "id" | "user_id":
                    value = int(value)
                case "beatmaps":
                    value = [BeatmapCache.deserialize(beatmap_cache) for beatmap_cache in literal_eval(value)]

            deserialized_dict[key] = value

        return cls.model_validate(deserialized_dict)
