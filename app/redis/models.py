from datetime import datetime
from ast import literal_eval

from pydantic import BaseModel

__all__ = [
    "QueueRequestHandlerTask",
    "BeatmapCache",
    "BeatmapsetCache"
]


class QueueRequestHandlerTask(BaseModel):
    user_id: int
    beatmapset_id: int
    queue_id: int
    comment: str
    mv_checked: bool
    completed_at: datetime | None = None

    def __hash__(self) -> int:
        return hash((self.queue_id, self.beatmapset_id))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QueueRequestHandlerTask):
            return NotImplemented

        return self.queue_id == other.queue_id and self.beatmapset_id == other.beatmapset_id

    def serialize(self) -> dict[str, str]:
        serialized_dict = {}

        for key, value in self.__dict__.items():
            match key:
                case "completed_at":
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
                case "completed_at":
                    value = datetime.fromisoformat(value) if value else None

            deserialized_dict[key] = value

        return QueueRequestHandlerTask.model_validate(deserialized_dict)


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

        return BeatmapCache.model_validate(deserialized_dict)


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

        return BeatmapsetCache.model_validate(deserialized_dict)
