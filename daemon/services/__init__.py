from enum import Enum
from typing import TypeVar

from .service import Service
from .score_fetcher import ScoreFetcher
from .profile_fetcher import ProfileFetcher

__all__ = [
    "ServiceType",
    "ServiceClass",
    "Service",
    "ScoreFetcher",
    "ProfileFetcher"
]

ServiceType = TypeVar("ServiceType", bound=Service)


class ServiceClass(Enum):
    SCORE_FETCHER = ScoreFetcher
    MAPPER_INFO_FETCHER = ProfileFetcher
