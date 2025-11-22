import logging

format = (
    '%(asctime)s - %(levelname)s - '
    '%(filename)s:%(lineno)d - %(funcName)s - %(message)s'
)
logging.basicConfig(
    format=format,
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG
)


class Logger:
    log = logging.getLogger()

    @staticmethod
    def info(msg: str) -> None:
        Logger.log.info(msg, stacklevel=2)

    @staticmethod
    def error(msg: str) -> None:
        Logger.log.error(msg, stacklevel=2)

    @staticmethod
    def warn(msg: str) -> None:
        Logger.log.warning(msg, stacklevel=2)

    @staticmethod
    def critical(msg: str) -> None:
        Logger.log.critical(msg, stacklevel=2)

    @staticmethod
    def exception(msg: str) -> None:
        Logger.log.exception(msg, stacklevel=2)
