import os
import logging
import traceback
from http import HTTPStatus
from flask import current_app, make_response
from flask_openapi3 import OpenAPI, Info, Tag
from pydantic import BaseModel, Field, ValidationError
from flask.wrappers import Response as FlaskResponse
from configparser import ConfigParser
from src.anonymizer_logic import anonymize_text_with_presidio
from pythonjsonlogger.json import JsonFormatter

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
            logging.getLogger().exception("Error building logger properties", extra={
                ERROR_MESSAGE: str(e),
                ERROR_TYPE: type(e).__name__,
                ERROR_STACK_TRACE: traceback.format_exc()
            })

    def filter(self, record):
        for key, value in self.ecs_fields.items():
            setattr(record, key, value)
        return True


ERROR_MESSAGE = "error.message"
ERROR_TYPE = "error.type"
ERROR_STACK_TRACE = "error.stack_trace"
logger = logging.getLogger()

handler = logging.StreamHandler()
formatter = JsonFormatter(
    '%(asctime)s %(levelname)s %(message)s %(service.name)s %(service.version)s %(service.environment)s '
    '%(error.type)s %(error.message)s %(error.stack_trace)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addFilter(ECSContextFilter())

log_level_str = os.getenv("APP_LOGGING_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
logger.setLevel(log_level)

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
        logger.exception("Error in /info endpoint", extra={
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
def anonymize_endpoint(body: AnonymizeRequest):
    """
    POST endpoint to anonymize the provided text.
    """
    try:
        input_text = body.text

        if not isinstance(input_text, str):
            logger.error("The 'text' field must be a string")
            return {"error": "The 'text' field must be a string"}, 400

        logger.debug("Start text anonymize")
        anonymized_text_output = anonymize_text_with_presidio(input_text)
        logger.debug("End text anonymize")

        return {"text": anonymized_text_output}, 200

    except Exception as e:
        logger.exception("Error in /anonymize endpoint", extra={
            ERROR_MESSAGE: str(e),
            ERROR_TYPE: type(e).__name__,
            ERROR_STACK_TRACE: traceback.format_exc()
        })
        return {"error": "An internal server error occurred"}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
