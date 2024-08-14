from enum import Enum


class RequestStatus(Enum):
    REJECTED = -1
    UNDETERMINED = 0
    ACCEPTED = 1


class RoleName(Enum):
    ADMIN = "admin"
