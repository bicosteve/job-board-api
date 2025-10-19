import logging

format = (
    '%(asctime)s-%(levelname)s-'
    '%(filename)s:%(lineno)d-%(funcName)s-%(message)s'
)
logging.basicConfig(
    format=format,
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG
)


class Loggger:
    log = logging.getLogger()

    @staticmethod
    def info(msg: str) -> None:
        Loggger.log.info(msg)

    @staticmethod
    def error(msg: str) -> None:
        Loggger.log.error(msg)

    @staticmethod
    def warn(msg: str) -> None:
        Loggger.log.warning(msg)

    @staticmethod
    def critical(msg: str) -> None:
        Loggger.log.critical(msg)

    @staticmethod
    def exception(msg: str) -> None:
        Loggger.log.exception(msg)
