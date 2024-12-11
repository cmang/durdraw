import durdraw.log as log
import time
from datetime import datetime, timedelta
import io
import json
import logging
import os
import time

def init_test_logger(name='test_log', **kwargs):
    fake_stream = io.StringIO()
    logger = log._getLogger(
        name,
        level='INFO',
        handlers=[logging.StreamHandler(fake_stream)],
        **kwargs
    )
    return logger, fake_stream

class TestLog:

    def test_log_complete_format(self):
        logger, fake_stream = init_test_logger()

        before = time.time()
        logger.info('Hello, world!')
        after = time.time()

        log_record = json.loads(fake_stream.getvalue())

        result = datetime.strptime(
            log_record['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z',
        )
        del log_record['timestamp']

        expected = {'msg': 'Hello, world!', 'level': 'INFO', 'name': 'durdraw.test_log', 'data': {}}

        assert log_record == expected
        assert before <= result.timestamp() <= after

    def test_log_timestamp_timezone_default_utc(self):
        logger, fake_stream = init_test_logger()
        logger.info('Hello, world!')
        log_record = json.loads(fake_stream.getvalue())['timestamp']

        result = datetime.strptime(
            log_record, '%Y-%m-%dT%H:%M:%S.%f%z',
        )
        assert result.utcoffset() == timedelta(0)

    def test_log_timestamp_timezone_local(self):
        # need to check that the code is actually producing local timezone
        # set the timezone temporarily in case someone is running the tests while in UTC
        os.environ['TZ'] = 'America/Boise'
        time.tzset()

        logger, fake_stream = init_test_logger(local_tz=True)
        logger.info('Hello, world!')
        log_record = json.loads(fake_stream.getvalue())['timestamp']

        result = datetime.strptime(
            log_record, '%Y-%m-%dT%H:%M:%S.%f%z',
        )
        assert result.utcoffset() is not None
        # this should be timedelta(days=-1, seconds=64800) during non-DST
        assert result.utcoffset() != timedelta(0)

    def test_log_no_args(self):
        logger, fake_stream = init_test_logger()
        logger.info('Hello, world!')

        result = json.loads(fake_stream.getvalue())
        del result['timestamp']

        assert result == {'msg': 'Hello, world!', 'level': 'INFO', 'name': 'durdraw.test_log', 'data': {}}

    def test_log_kwargs(self):
        logger, fake_stream = init_test_logger()
        logger.info('Hello, world!', {'key1': 'value1', 'key2': 'value2'})

        result = json.loads(fake_stream.getvalue())
        del result['timestamp']

        assert result == {'msg': 'Hello, world!', 'level': 'INFO', 'name': 'durdraw.test_log', 'data': {'key1': 'value1', 'key2': 'value2'}}

    def test_log_to_file(self):
        if os.path.exists('test_log.log'):
            os.remove('test_log.log')

        logger = log.getLogger('test_log', level='INFO', filepath='test_log.log', override=True)
        logger.info('Hello, world!')

        assert os.path.exists('test_log.log')

        with open('test_log.log', 'r') as file:
            result = json.loads(file.read())
            del result['timestamp']
        os.remove('test_log.log')

        assert result == {
            'msg': 'Hello, world!',
            'level': 'INFO',
            'name': 'durdraw.test_log',
            'data': {},
        }

    def test_log_no_emit(self):
        if os.path.exists('test_log.log'):
            os.remove('test_log.log')

        logger = log.getLogger('test_log', level='CRITICAL', filepath='test_log.log', override=True)
        logger.info('Hello, world!')

        # the file should not exist, as the level is set to CRITICAL
        assert not os.path.exists('test_log.log')

        # the file should be created, as the level is set to CRITICAL
        logger.critical('Hello, world!')
        assert os.path.exists('test_log.log')

        with open('test_log.log', 'r') as file:
            result = json.loads(file.read())
            del result['timestamp']
        os.remove('test_log.log')

        assert result == {
            'msg': 'Hello, world!',
            'level': 'CRITICAL',
            'name': 'durdraw.test_log',
            'data': {},
        }

    def test_multiple_loggers(self):
        '''Test that child loggers with different names don't produce duplicate logs'''

        if os.path.exists('test_log.log'):
            os.remove('test_log.log')

        logger1 = log.getLogger('test_log', level='INFO', filepath='test_log.log', override=True)
        logger2 = log.getLogger('test_log2', level='INFO', filepath='test_log.log', override=False)

        logger1.info('Hello, world!')
        logger2.info('Hello, world!')

        with open('test_log.log', 'r') as file:
            results = list(map(json.loads, file))
        for result in results:
            del result['timestamp']
        os.remove('test_log.log')

        assert results == [
            {
                'msg': 'Hello, world!',
                'level': 'INFO',
                'name': 'durdraw.test_log',
                'data': {},
            },
            {
                'msg': 'Hello, world!',
                'level': 'INFO',
                'name': 'durdraw.test_log2',
                'data': {},
            },
        ]

    def test_reuse_loggers(self):
        '''Test that child loggers with the same name don't produce duplicate logs'''

        if os.path.exists('test_log.log'):
            os.remove('test_log.log')

        logger1 = log.getLogger('test_log', level='INFO', filepath='test_log.log', override=True)
        logger2 = log.getLogger('test_log', level='INFO', filepath='test_log.log', override=False)

        logger1.info('Hello, world!')
        logger2.info('Hello, world!')

        with open('test_log.log', 'r') as file:
            results = list(map(json.loads, file))
        for result in results:
            del result['timestamp']
        os.remove('test_log.log')

        assert results == [
            {
                'msg': 'Hello, world!',
                'level': 'INFO',
                'name': 'durdraw.test_log',
                'data': {},
            },
            {
                'msg': 'Hello, world!',
                'level': 'INFO',
                'name': 'durdraw.test_log',
                'data': {},
            },
        ]
