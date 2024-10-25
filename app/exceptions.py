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
