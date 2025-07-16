import logging
import os
import unittest
from unittest.mock import patch, MagicMock

from src.logging_setup import ECSContextFilter, NonNullJsonFormatter, on_starting


class TestECSContextFilter(unittest.TestCase):
    @patch('src.logging_setup.ConfigParser')
    @patch.dict(os.environ, {"ENV": "test-environment"})
    def test_filter_sets_ecs_fields(self, mock_config_parser):
        # mock setup.cfg
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key: f"{key}-value"
        mock_config_parser.return_value = mock_config

        filter_instance = ECSContextFilter()
        mock_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )

        result = filter_instance.filter(mock_record)

        self.assertTrue(result)
        self.assertEqual(mock_record.__dict__["service.name"], "name-value")
        self.assertEqual(mock_record.__dict__["service.version"], "version-value")
        self.assertEqual(mock_record.__dict__["service.environment"], "test-environment")


class TestNonNullJsonFormatter(unittest.TestCase):
    def test_formatter_removes_none_and_adds_timestamp(self):
        formatter = NonNullJsonFormatter()
        log_record = {
            "message": "Hello world",
            "error.message": None,
            "custom": 123
        }
        formatted = formatter.process_log_record(log_record)

        self.assertIn("message", formatted)
        self.assertIn("custom", formatted)
        self.assertIn("@timestamp", formatted)
        self.assertNotIn("error.message", formatted)
        self.assertIsInstance(formatted["@timestamp"], str)


class TestLoggingSetup(unittest.TestCase):
    def test_on_starting_applies_configuration(self):
        os.environ["APP_LOGGING_LEVEL"] = "INFO"
        on_starting(server=None)

        root_logger = logging.getLogger()
        assert root_logger.getEffectiveLevel() == logging.INFO


if __name__ == '__main__':
    unittest.main()
