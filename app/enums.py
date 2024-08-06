from enum import Enum


class RequestStatus(Enum):
    REJECTED = -1
    UNDETERMINED = 0
    ACCEPTED = 1
