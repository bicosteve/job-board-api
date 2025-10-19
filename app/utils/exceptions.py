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


class InvalidPasswordResetError(Exception):
    '''Raised when user tries to use wrong token to reset password'''
    pass


class GenericRedisError(Exception):
    '''Raised when an issue occurs because of Redis'''
    pass


class GenericGenerateResetTokenError(Exception):
    '''Raised when an error occurs while generating reset token'''
    pass


class GenericPasswordHashError(Exception):
    '''Raised when there is a problem hashing password'''
    pass
