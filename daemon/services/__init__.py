from enum import Enum
from typing import TypeVar

from .service import Service
from .score_fetcher import ScoreFetcher
from .mapper_info_fetcher import MapperInfoFetcher

__all__ = [
    "ServiceType",
    "ServiceClass",
    "Service",
    "ScoreFetcher",
    "MapperInfoFetcher"
]

ServiceType = TypeVar("ServiceType", bound=Service)


class ServiceClass(Enum):
    SCORE_FETCHER = ScoreFetcher
    MAPPER_INFO_FETCHER = MapperInfoFetcher
