import os
import logging
import traceback
import json
import time
import uuid
from http import HTTPStatus
from flask import current_app, make_response, g
from flask_openapi3 import OpenAPI, Info, Tag
from pydantic import BaseModel, Field, ValidationError
from flask.wrappers import Response as FlaskResponse
from configparser import ConfigParser
from src.anonymizer_logic import anonymize_text_with_presidio
from pythonjsonlogger.json import JsonFormatter
from functools import wraps





ERROR_MESSAGE = "error.message"
ERROR_TYPE = "error.type"
ERROR_STACK_TRACE = "error.stack_trace"

# OpenAPI metadata
info = Info(title="Anonymizer API", version="1.0.0")
info_tag = Tag(name="Info", description="Liveness & readiness endpoints")
anonymize_tag = Tag(name="Anonymize", description="Text anonymization endpoints")

api_key = {
    "type": "apiKey",
    "name": "api_key",
    "in": "header"
}
security_schemes = {"api_key": api_key}
security = [{"api_key": []}]


class AnonymizeRequest(BaseModel):
    text: str = Field(..., description="Text to be anonymized")


class AnonymizeResponse(BaseModel):
    text: str = Field(..., description="Anonymized text")


class InfoResponse(BaseModel):
    name: str
    version: str
    environment: str


class ErrorResponse(BaseModel):
    error: str


def validation_error_callback(e: ValidationError) -> FlaskResponse:
    validation_error_object = ErrorResponse(error="Missing required field 'text'")
    response = make_response(validation_error_object.model_dump_json())
    response.headers["Content-Type"] = "application/json"
    response.status_code = getattr(current_app, "validation_error_status", HTTPStatus.BAD_REQUEST)
    return response


app = OpenAPI(
    __name__,
    info=info,
    security_schemes=security_schemes,
    validation_error_status=HTTPStatus.BAD_REQUEST,
    validation_error_model=ErrorResponse,
    validation_error_callback=validation_error_callback)


# Define logger
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
            app.logger.exception("Error building logger properties", extra={
                ERROR_MESSAGE: str(e),
                ERROR_TYPE: type(e).__name__,
                ERROR_STACK_TRACE: traceback.format_exc()
            })

    def filter(self, record):
        for key, value in self.ecs_fields.items():
            setattr(record, key, value)
        return True


formatter = JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s '
    '%(service.name)s %(service.version)s %(service.environment)s '
    '%(error.type)s %(error.message)s %(error.stack_trace)s '
    '%(method)s %(startTime)s %(requestId)s %(operationId)s %(args)s '
    '%(responseTime)s %(status)s %(httpCode)s %(response)s',
    rename_fields={
        "asctime": "@timestamp",
        "levelname": "log.level",
        "name": "log.logger",
    }
)
log_level_str = os.getenv("APP_LOGGING_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    gunicorn_logger.setLevel(log_level)
    app.logger.setLevel(gunicorn_logger.level)
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)
        handler.addFilter(ECSContextFilter())
else:
    app.logger.setLevel(log_level)


def ecs_logger(method_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time_ms = int(time.time() * 1000)
            request_id = str(uuid.uuid4())
            operation_id = str(uuid.uuid4())

            # Prepare extra fields
            g.extra_fields = {
                "method": method_name,
                "startTime": start_time_ms,
                "requestId": request_id,
                "operationId": operation_id,
                "args": "",
            }

            try:
                app.logger.info(f"Invoking API operation {method_name}", extra=g.extra_fields)

                # Execute the function
                result = func(*args, **kwargs)
                end_time_ms = int(time.time() * 1000)
                response_time = end_time_ms - start_time_ms

                if isinstance(result, FlaskResponse):
                    status_code = result.status_code
                else:
                    status_code = 200

                if status_code == 200:
                    # Log success
                    app.logger.info(f"Successful API operation {method_name}", extra={
                        **g.extra_fields,
                        "responseTime": response_time,
                        "status": "OK",
                        "httpCode": 200,
                        "response": json.dumps(result if isinstance(result, dict) else {"result": result})
                    })
                else:
                    body = result.get_data(as_text=True)
                    json_data = json.loads(body)
                    error = json_data.get("error")
                    app.logger.exception(f"Failed API operation {method_name}", extra={
                        **g.extra_fields,
                        "status": "KO",
                        "httpCode": status_code,
                        "faultCode": HTTPStatus(status_code).name,
                        "faultDetail": error
                    })

                return result

            except Exception as e:
                app.logger.exception(f"Failed API operation {method_name}", extra={
                    **g.extra_fields,
                    "status": "KO",
                    "httpCode": 500,
                    "faultCode": "UNEXPECTED_ERROR",
                    "faultDetail": str(e),
                })
                raise e

        return wrapper

    return decorator


@app.get(
    '/info',
    tags=[info_tag],
    responses={
        HTTPStatus.OK: InfoResponse,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorResponse,
    },
    summary="Get application info",
    description="Liveness & readiness endpoint. Returns application name, version, and environment.",
    security=security
)
@ecs_logger("info")
def info():
    """
    GET endpoint for liveness & readiness
    """
    try:
        config = ConfigParser()
        config.read('setup.cfg')
        app_name = config.get("metadata", "name")
        app_version = config.get("metadata", "version")
        return {"name": app_name, "version": app_version, "environment": os.getenv("ENV", "not specified")}, 200

    except Exception as e:
        app.logger.exception("Error in /info endpoint", extra={
            **g.extra_fields,
            ERROR_MESSAGE: str(e),
            ERROR_TYPE: type(e).__name__,
            ERROR_STACK_TRACE: traceback.format_exc()
        })
        return {"error": "An internal server error occurred"}, 500


@app.post(
    '/anonymize',
    tags=[anonymize_tag],
    responses={
        HTTPStatus.OK: AnonymizeResponse,
        HTTPStatus.BAD_REQUEST: ErrorResponse,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorResponse,
    },
    summary="Anonymize text",
    description="Anonymizes the provided text using Presidio.",
    security=security
)
@ecs_logger("anonymize_endpoint")
def anonymize_endpoint(body: AnonymizeRequest):
    """
    POST endpoint to anonymize the provided text.
    """
    try:
        input_text = body.text

        if not isinstance(input_text, str):
            app.logger.error("The 'text' field must be a string", extra=g.extra_fields)
            return {"error": "The 'text' field must be a string"}, 400

        app.logger.debug("Start text anonymize", extra=g.extra_fields)
        anonymized_text_output = anonymize_text_with_presidio(input_text)
        app.logger.debug("End text anonymize", extra=g.extra_fields)

        return {"text": anonymized_text_output}, 200

    except Exception as e:
        app.logger.exception("Error in /anonymize endpoint", extra={
            **g.extra_fields,
            ERROR_MESSAGE: str(e),
            ERROR_TYPE: type(e).__name__,
            ERROR_STACK_TRACE: traceback.format_exc()
        })
        return {"error": "An internal server error occurred"}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
