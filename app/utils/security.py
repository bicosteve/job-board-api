import bcrypt


class Security:
    @staticmethod
    def hash_password(password) -> str:
        """
        Hash plain text password using bcrypt.
        Returns the hashed password as a UTF-8 string.
        """
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hash.decode("utf-8")

    @staticmethod
    def check_password(plain_password, hash) -> bool:
        """
        Verifies the plain password against the hashed password.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hash.encode("utf-8"),
        )
