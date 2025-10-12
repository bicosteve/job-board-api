import random


class Helpers:
    @staticmethod
    def generate_verification_code():
        return str(random.randint(100_000, 999_999))
