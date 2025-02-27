from enum import Enum


class RequestStatus(Enum):
    REJECTED = -1
    UNDETERMINED = 0
    ACCEPTED = 1


class RoleName(Enum):
    ADMIN = "admin"
    PRIVILEGED = "privileged"


class QueueVisibility(Enum):
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2
