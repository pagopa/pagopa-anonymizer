import os
import traceback
import json
import time
import uuid
from http import HTTPStatus
from flask import current_app, make_response, g
from flask_openapi3 import OpenAPI, Info, Tag, Server, ServerVariable
from pydantic import BaseModel, Field, ValidationError
from flask.wrappers import Response as FlaskResponse
from configparser import ConfigParser
from src.anonymizer_logic import anonymize_text_with_presidio
from functools import wraps

ERROR_MESSAGE = "error.message"
ERROR_TYPE = "error.type"
ERROR_STACK_TRACE = "error.stack_trace"


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

servers = [
    Server(url="http://localhost:8080"),
    Server(url="https://{host}{basePath}", variables={
        "basePath": ServerVariable(
            default="/anonymizer/v1",
            enum=[
                "anonymizer/v1"
            ]),
        "host": ServerVariable(
            default="https://api.platform.pagopa.it",
            enum=[
                "https://api.dev.platform.pagopa.it",
                "https://api.uat.platform.pagopa.it",
                "https://api.platform.pagopa.it"
            ])
    })
]

app = OpenAPI(
    __name__,
    info=info,
    servers=servers,
    security_schemes=security_schemes,
    validation_error_status=HTTPStatus.BAD_REQUEST,
    validation_error_model=ErrorResponse,
    validation_error_callback=validation_error_callback
)


def serialize_kwargs(kwargs):
    serialized = {}
    for k, v in kwargs.items():
        if hasattr(v, 'model_dump'):
            serialized[k] = v.model_dump()
        elif hasattr(v, 'dict'):
            serialized[k] = v.dict()
        else:
            serialized[k] = v
    return json.dumps(serialized)


# Wrap API method to log execution metadata
def execution_logging_decorator(method_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Executes the decorated function while capturing and logging execution metadata.

            Args:
                *args: Wrapped function's positional arguments (e.g., values).
                **kwargs: Wrapped function's named arguments (e.g., key=value).

            Returns:
                The result of the original function, typically a (body, status_code) tuple.
            """
            start_time_ms = int(time.time() * 1000)
            request_id = str(uuid.uuid4())
            operation_id = str(uuid.uuid4())

            # Prepare extra fields
            g.extra_fields = {
                "method": method_name,
                "startTime": start_time_ms,
                "requestId": request_id,
                "operationId": operation_id,
                "_request_args": "{}"
                # Set _request_args to {} to prevent logging sensitive personal data (PII)
                # "_request_args": "{}" if not kwargs else serialize_kwargs(kwargs)
            }

            try:
                app.logger.info("Invoking API operation " + method_name, extra=g.extra_fields)

                # Execute the wrapped function
                response = func(*args, **kwargs)
                end_time_ms = int(time.time() * 1000)
                response_time = end_time_ms - start_time_ms

                body, status_code = response

                if status_code == 200:
                    app.logger.info("Successful API operation %s", method_name, extra={
                        **g.extra_fields,
                        "responseTime": response_time,
                        "status": "OK",
                        "httpCode": 200,
                        "response": "{}" if not body else json.dumps(body)
                    })
                else:
                    error = body.get("error")
                    app.logger.info("Failed API operation %s", method_name, extra={
                        **g.extra_fields,
                        "status": "KO",
                        "httpCode": status_code,
                        "faultCode": HTTPStatus(status_code).name,
                        "faultDetail": error
                    })

                return response

            except Exception as e:
                app.logger.exception("Failed API operation %s", method_name, extra={
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
@execution_logging_decorator("info")
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
@execution_logging_decorator("anonymize_endpoint")
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
