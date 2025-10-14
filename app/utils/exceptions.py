class InvalidCredentialsError(Exception):
    """Raised when user provides invalid email or password"""

    pass


class UserExistError(Exception):
    """Raised when user tries to register twice"""

    pass


class GenericDatabaseError(Exception):
    """Raised when tables operations fail"""

    pass


class InvalidLoginAttemptError(Exception):
    """Raised when user tries to log into unverified account"""

    pass
