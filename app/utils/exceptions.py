class InvalidCredentialsError(Exception):
    """Raised when user provides invalid email or password"""


class UserExistError(Exception):
    """Raised when user tries to register twice"""


class UserDoesNotExistError(Exception):
    """Raised when user is not found"""


class GenericDatabaseError(Exception):
    """Raised when tables operations fail"""


class InvalidLoginAttemptError(Exception):
    """Raised when user tries to log into unverified account"""


class InvalidPasswordResetError(Exception):
    '''Raised when user tries to use wrong token to reset password'''


class GenericRedisError(Exception):
    '''Raised when an issue occurs because of Redis'''


class GenericGenerateResetTokenError(Exception):
    '''Raised when an error occurs while generating reset token'''


class GenericPasswordHashError(Exception):
    '''Raised when there is a problem hashing password'''


class GenericGenerateAuthTokenError(Exception):
    '''Raised when there is a problem generating auth token'''
