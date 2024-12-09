import durdraw.log as log
import time
from datetime import datetime
import io
import json
import logging

class TestLog:
    def test_log_complete_format(self):
        fake_stream = io.StringIO()

        logger = log._getLogger("test_log", level=logging.INFO, handlers=[logging.StreamHandler(fake_stream)])

        before = time.time()
        logger.info("Hello, world!")
        after = time.time()

        result = fake_stream.getvalue()
        log_record = json.loads(result)

        timestamp = datetime.fromisoformat(log_record["timestamp"]).timestamp()
        del log_record["timestamp"]

        expected = {'msg': 'Hello, world!', 'data': {}}

        assert log_record == expected
        assert before <= timestamp <= after

    def test_log_timestamp_timezone(self):
        fake_stream = io.StringIO()
        logger = log._getLogger("test_log", level=logging.INFO, handlers=[logging.StreamHandler(fake_stream)])
        logger.info("Hello, world!")

        result = datetime.fromisoformat(json.loads(fake_stream.getvalue())["timestamp"])

        assert result.utcoffset() is not None
        assert result.utcoffset().seconds == time.localtime().tm_gmtoff

    def test_log_no_args(self):
        fake_stream = io.StringIO()
        logger = log._getLogger("test_log", level=logging.INFO, handlers=[logging.StreamHandler(fake_stream)])
        logger.info("Hello, world!")

        result = json.loads(fake_stream.getvalue())
        del result["timestamp"]

        assert result == {'msg': 'Hello, world!', 'data': {}}

    def test_log_args(self):
        fake_stream = io.StringIO()
        logger = log._getLogger("test_log", level=logging.INFO, handlers=[logging.StreamHandler(fake_stream)])
        logger.info("Hello, world!", 1, 2, 3)

        result = json.loads(fake_stream.getvalue())
        del result["timestamp"]

        assert result == {'msg': 'Hello, world!', 'data': {'args': [1, 2, 3]}}

    def test_log_kwargs(self):
        fake_stream = io.StringIO()
        logger = log._getLogger("test_log", level=logging.INFO, handlers=[logging.StreamHandler(fake_stream)])
        logger.info("Hello, world!", {"key1": "value1", "key2": "value2"})

        result = json.loads(fake_stream.getvalue())
        del result["timestamp"]

        assert result == {'msg': 'Hello, world!', 'data': {'key1': 'value1', 'key2': 'value2'}}

    def test_log_args_kwargs(self):
        fake_stream = io.StringIO()
        logger = log._getLogger("test_log", level=logging.INFO, handlers=[logging.StreamHandler(fake_stream)])
        logger.info("Hello, world!", 1, 2, 3, {"key1": "value1", "key2": "value2"})

        result = json.loads(fake_stream.getvalue())
        del result["timestamp"]

        assert result == {'msg': 'Hello, world!', 'data': {'args': [1, 2, 3], 'key1': 'value1', 'key2': 'value2'}}

