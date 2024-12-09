import durdraw.log as log
import time
from datetime import datetime
import io
import json
import logging
import os

def init_test_logger(**kwargs):
    fake_stream = io.StringIO()
    logger = log._getLogger(
        'test_log',
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

        result = fake_stream.getvalue()
        log_record = json.loads(result)

        timestamp = datetime.fromisoformat(log_record['timestamp']).timestamp()
        del log_record['timestamp']

        expected = {'msg': 'Hello, world!', 'level': 'INFO', 'name': 'durdraw.test_log', 'data': {}}

        assert log_record == expected
        assert before <= timestamp <= after

    def test_log_timestamp_timezone(self):
        logger, fake_stream = init_test_logger()
        logger.info('Hello, world!')

        result = datetime.fromisoformat(json.loads(fake_stream.getvalue())['timestamp'])

        assert result.utcoffset() is not None
        assert result.utcoffset().seconds == time.localtime().tm_gmtoff

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
