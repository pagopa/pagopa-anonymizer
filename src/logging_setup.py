import os
import logging
import traceback
from logging.config import dictConfig
from pythonjsonlogger.json import JsonFormatter
from configparser import ConfigParser
from datetime import datetime, timezone

ERROR_MESSAGE = "error.message"
ERROR_TYPE = "error.type"
ERROR_STACK_TRACE = "error.stack_trace"

# Define logger filter
class ECSContextFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        try:
            config = ConfigParser()
            config.read('setup.cfg')
            self.ecs_fields = {
                "service.name": config.get("metadata", "name"),
                "service.version": config.get("metadata", "version"),
                "service.environment": os.getenv("ENV", "not specified"),
            }
        except Exception as e:
            logging.getLogger('').exception("Error building logger properties", extra={
                ERROR_MESSAGE: str(e),
                ERROR_TYPE: type(e).__name__,
                ERROR_STACK_TRACE: traceback.format_exc()
            })

    def filter(self, record):
        for key, value in self.ecs_fields.items():
            setattr(record, key, value)
        return True

# Define a JsonFormatter that filter out null fields
class NonNullJsonFormatter(JsonFormatter):
    def process_log_record(self, log_record):
        # Format timestamp in ISO 8601
        log_record['@timestamp'] = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

        # Filter null fields
        return {k: v for k, v in log_record.items() if v is not None}


# Configure logging
def on_starting(server):
    log_level_str = os.getenv("APP_LOGGING_LEVEL", "INFO").upper()

    dictConfig({
        'version': 1,
        'formatters': {
            'json': {
                '()': NonNullJsonFormatter,
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s '
                          '%(service.name)s %(service.version)s %(service.environment)s '
                          '%(error.type)s %(error.message)s %(error.stack_trace)s '
                          '%(method)s %(startTime)s %(requestId)s %(operationId)s %(_request_args)s '
                          '%(responseTime)s %(status)s %(httpCode)s %(response)s',
                'rename_fields': {
                    "asctime": "@timestamp",
                    "levelname": "log.level",
                    "name": "log.logger",
                    "_request_args": "args",
                }
            },
        },
        'filters': {
            'ecs_context_filter': {
                '()': ECSContextFilter,
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'json',
                'filters': ['ecs_context_filter'],
            },
        },
        'loggers': {
            'gunicorn': {
                'handlers': ['console'],
                'level': log_level_str,
                'propagate': False,
            },
            'flask.app': {
                'handlers': ['console'],
                'level': log_level_str,
                'propagate': False,
            }
        },
        'root': {
            'level': log_level_str,
            'handlers': ['console']
        }
    })
    logger = logging.getLogger(__name__)
    logger.info("🔥 Logging configured on Gunicorn startup")