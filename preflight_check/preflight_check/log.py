import logging
from enum import Enum

import rich


class LogLevel(int, Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __str__(self) -> str:
        return self.name


class Logger:
    logger: rich.console.Console
    level: LogLevel

    def __init__(self, level: LogLevel = LogLevel.INFO) -> None:
        self.logger = rich.console.Console()
        self.level = level

    def debug(self, message: str) -> None:
        self._log(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        self._log(LogLevel.INFO, message)

    def warning(self, message: str) -> None:
        self._log(LogLevel.WARNING, message)

    def error(self, message: str) -> None:
        self._log(LogLevel.ERROR, message)

    def set_level(self, level: LogLevel) -> None:
        self.level = level

    def _log(self, level: LogLevel, message: str) -> None:
        if level <= self.level:
            self.logger.log(f"[{level}] {message}")


log = Logger()


def set_level(level: LogLevel) -> None:
    log.set_level(level)


def debug(message: str) -> None:
    log.debug(message)


def info(message: str) -> None:
    log.info(message)


def warning(message: str) -> None:
    log.warning(message)


def error(message: str) -> None:
    log.error(message)
