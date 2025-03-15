from datetime import datetime


class TypeValidationError(TypeError):
    def __init__(self, value_type: type, *target_types: type, message: str = None):
        self.value_type = value_type
        self.target_types = target_types
        self.message = message if message is not None else f"Expected type(s) {self.expected_types}, but got {value_type.__name__}"

        super().__init__(self.message)

    @property
    def expected_types(self) -> str:
        return ", ".join(t.__name__ for t in self.target_types)


class RestrictedUserError(ValueError):
    def __init__(self, user_id: int, message: str = None):
        self.user_id = user_id
        self.message = message if message is not None else f"User {self.user_id} is either restricted, deleted, or otherwise inaccessible"


class RateLimitExceeded(Exception):
    def __init__(self, next_window: datetime, message: str = None):
        self.next_window = next_window

        if message is None:
            message = f"Rate limit exceeded. Try again in {self.remaining_time:.2f} seconds."

        super().__init__(message)

    @property
    def remaining_time(self) -> float:
        return (self.next_window - datetime.now()).total_seconds()
