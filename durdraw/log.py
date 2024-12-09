'''
code taken from: github.com/tmck-code/pp/log/log.py

A module to create loggers with custom handlers and a custom formatter.

usage examples to initialise a logger:
    ```python
    # initialise logger to file:
    logger = getLogger('my_logger', level=logging.DEBUG, filename='my_log.log')
    ```

usage examples to log messages:
    ```python
    logger.info('This is a basic info message')
    # {"timestamp": "2024-12-09T15:05:43.904417", "msg": "This is a basic info message", "data": {}}

    logger.info('This is an info message', {'key': 'value'})
    # {"timestamp": "2024-12-09T15:05:43.904600", "msg": "This is an info message", "data": {"key": "value"}}

    logger.debug('This is a debug message', 'arg1', 'arg2', {'key': 'value'})
    # {"timestamp": "2024-12-09T15:05:43.904749", "msg": "This is a debug message", "data": {"args": ["arg1", "arg2"], "key": "value"}}
    ```
'''

from dataclasses import asdict, dataclass, is_dataclass, field
from datetime import datetime
import io
import json
import logging
import sys

LOG_ROOT_NAME = 'durdraw'
DEFAULT_LOG_FILEPATH = '/tmp/durdraw.log'

# log levels
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

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

        args, kwargs = None, {}
        if isinstance(record.args, tuple):
            if len(record.args) == 1:
                args = record.args
            elif len(record.args) > 1:
                if isinstance(record.args[-1], dict):
                    args, kwargs = record.args[:-1], record.args[-1]
                else:
                    args = record.args
        elif isinstance(record.args, dict):
            kwargs = record.args

        record.msg = json.dumps(
            {
                'timestamp': datetime.now().astimezone().isoformat(),
                'msg':       record.msg,
                'data':      {
                    **({'args': args} if args else {}),
                    **(kwargs if kwargs else {}),
                }
            },
            default=_json_default,
        )
        record.args = ()
        return super().format(record)


def _getLogger(name: str, level: int = logging.CRITICAL, handlers: list[logging.Handler] = []) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - If no handlers are provided, the logger will not output any logs.
    - This function requires the handlers to be initialized when passed as args.
    - the same log level is applied to all handlers.
    '''

    # create the logger
    logger = logging.getLogger(LOG_ROOT_NAME)
    logger.setLevel(level)
    # close/remove any existing handlers
    while logger.handlers:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

    # create the logger
    logger = logging.getLogger(f'{LOG_ROOT_NAME}.{name}')
    logger.setLevel(level)

    # close/remove any existing handlers
    while logger.handlers:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

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
    Logger(name, level, handlers, print_stream, filename)
    '''
    name: str
    level: int = logging.CRITICAL
    filename: str = DEFAULT_LOG_FILEPATH
    handlers: list[logging.Handler] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.handlers.append(logging.FileHandler(self.filename))

    def getLogger(self) -> logging.Logger:
        return _getLogger(self.name, self.level, handlers=self.handlers)

    @property
    def logger(self) -> logging.Logger:
        return self.getLogger()


def getLogger(name: str, level: int = logging.CRITICAL, filename: str = DEFAULT_LOG_FILEPATH) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - if `print_stream` is provided, the logger will output logs to it.
    - if `filename` is provided, the logger will output logs to it.
    - if both are provided, the logger will output logs to both.
    - if neither are provided, the logger will not output any logs.
    '''
    return _getLogger(name, level, [logging.FileHandler(filename)])
