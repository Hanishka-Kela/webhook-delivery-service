class PasswordMismatchError(ValueError):
    """Raised when password and confirmation do not match."""


class UserAlreadyExistsError(ValueError):
    """Raised when a user with the given email already exists."""
