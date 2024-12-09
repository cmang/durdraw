'''
code taken from: github.com/tmck-code/pp/log/log.py

A module to create loggers with custom handlers and a custom formatter.

usage examples to initialise a logger:
    ```python
    # initialise logger to file:
    logger = getLogger('my_logger', level=logging.DEBUG, filepath='./my_log.log')
    ```

usage examples to log messages:
1. log a basic info message by passing a string:
    ```python
    logger.info('This is a basic info message')
    # {"timestamp": "2024-12-09T15:05:43.904417", "msg": "This is a basic info message", "data": {}}
    ```
2. log a message with additional data by passing a dictionary as the second argument:
    ```python
    logger.info('This is an info message', {'key': 'value'})
    # {"timestamp": "2024-12-09T15:05:43.904600", "msg": "This is an info message", "data": {"key": "value"}}
'''

from dataclasses import asdict, dataclass, is_dataclass, field
from datetime import datetime
import io
import json
import logging
import sys
from typing import TypeAlias, Literal
from types import MappingProxyType

CRITICAL: int = logging.CRITICAL
ERROR:    int = logging.ERROR
WARNING:  int = logging.WARNING
INFO:     int = logging.INFO
DEBUG:    int = logging.DEBUG

LOG_LEVEL_NAME: TypeAlias = Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
LOG_LEVEL_VALUE: TypeAlias = Literal[CRITICAL, ERROR, WARNING, INFO, DEBUG]

LOG_LEVEL: MappingProxyType[LOG_LEVEL_NAME, LOG_LEVEL_VALUE] = MappingProxyType({
    'CRITICAL': CRITICAL,
    'ERROR':    ERROR,
    'WARNING':  WARNING,
    'INFO':     INFO,
    'DEBUG':    DEBUG,
})

LOG_ROOT_NAME = 'durdraw'
DEFAULT_LOG_FILEPATH = './durdraw.log'
DEFAULT_LOG_LEVEL = 'WARNING'

def _json_default(obj: object) -> str:
    'Default JSON serializer, supports most main class types'
    if isinstance(obj, str):       return obj
    if is_dataclass(obj):          return asdict(obj)
    if isinstance(obj, datetime):  return obj.isoformat()
    if hasattr(obj, '__dict__'):   return obj.__dict__
    if hasattr(obj, '__name__'):   return obj.__name__
    if hasattr(obj, '__slots__'):  return {k: getattr(obj, k) for k in obj.__slots__}
    if hasattr(obj, '_asdict'):    return obj._asdict()
    return str(obj)


class LogFormatter(logging.Formatter):
    'Custom log formatter that formats log messages as JSON, aka "Structured Logging".'

    def format(self, record) -> str:
        'Formats the log message as JSON.'

        kwargs = {}
        if isinstance(record.args, dict):
            kwargs = record.args

        record.msg = json.dumps(
            {
                'timestamp': datetime.now().astimezone().isoformat(),
                'level':     record.levelname,
                'name':      record.name,
                'msg':       record.msg,
                'data':      kwargs,
            },
            default=_json_default,
        )
        return super().format(record)


def _getLogger(name: str, level: int = logging.CRITICAL, handlers: list[logging.Handler] = []) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - If no handlers are provided, the logger will not output any logs.
    - This function requires the handlers to be initialized when passed as args.
    - the same log level is applied to all handlers.
    '''

    # create the logger
    logger = logging.getLogger(f'{LOG_ROOT_NAME}.{name}')
    logger.setLevel(level)

    # add the new handlers
    for handler in handlers:
        handler.setLevel(level)
        logger.addHandler(handler)

    if logger.handlers:
        # only set the first handler to use the custom formatter
        logger.handlers[0].setFormatter(LogFormatter())

    return logger


@dataclass
class Logger:
    '''
    A class to create a logger with custom handlers and a custom formatter.
    Logger(name, level, handlers, print_stream, filepath)
    '''
    name: str
    level: int = logging.CRITICAL
    filepath: str = DEFAULT_LOG_FILEPATH
    handlers: list[logging.Handler] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.handlers.append(logging.FileHandler(self.filepath))

    def getLogger(self) -> logging.Logger:
        return _getLogger(self.name, self.level, handlers=self.handlers)

    @property
    def logger(self) -> logging.Logger:
        return self.getLogger()


def getLogger(name: str, level: LOG_LEVEL_NAME = DEFAULT_LOG_LEVEL, filepath: str = DEFAULT_LOG_FILEPATH) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - disable the logger by setting the level to logging.CRITICAL
    - the default log level is 'WARNING'
    - the default log file is './durdraw.log'

    This logger will only create an output file if there is a call to write a log message that matches the log level.
    '''
    return _getLogger(
        name,
        level=LOG_LEVEL[level],
        handlers=[logging.FileHandler(filepath, mode='a', delay=True)]
    )

