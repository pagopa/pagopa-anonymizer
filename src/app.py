from http import HTTPStatus
from flask import current_app, make_response, request, g
from flask_openapi3 import OpenAPI, Info, Tag
from pydantic import BaseModel, Field, ValidationError
from flask.wrappers import Response as FlaskResponse
from configparser import ConfigParser
import os
from anonymizer_logic import anonymize_text_with_presidio
from pythonjsonlogger import json
import logging
import uuid


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
    # Aggiungiamo il logging anche qui, usando il request_id
    current_app.logger.warning(
        "Request validation failed",
        extra={"validation_errors": e.errors()}
    )
    validation_error_object = ErrorResponse(error="Missing required field 'text'")
    response = make_response(validation_error_object.model_dump_json())
    response.headers["Content-Type"] = "application/json"
    response.status_code = getattr(current_app, "validation_error_status", HTTPStatus.BAD_REQUEST)
    return response

# <-- NUOVO: Creiamo un formatter personalizzato per aggiungere campi dinamicamente -->
class CustomJsonFormatter(json.JsonFormatter):
    def __init__(self, *args, **kwargs):
        # Aggiungiamo la rinomina dei campi al costruttore
        kwargs['rename_fields'] = {'levelname': 'log.level'}
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        # Aggiunge il request_id se è disponibile nel contesto della richiesta
        if g and hasattr(g, 'request_id'):
            log_record['request_id'] = g.request_id
        config = ConfigParser()
        config.read('setup.cfg')
        app_name = config.get("metadata", "name")
        app_version = config.get("metadata", "version")
        log_record['service.name']=app_name
        log_record['service.version']=app_version

# --- Inizio configurazione app ---
app = OpenAPI(
    __name__,
    info=info,
    security_schemes=security_schemes,
    validation_error_status=HTTPStatus.BAD_REQUEST,
    validation_error_model=ErrorResponse,
    validation_error_callback=validation_error_callback)

# --- Configurazione del logging (modificata) ---
app.logger.handlers.clear()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()

# <-- MODIFICATO: Usiamo il nostro formatter personalizzato -->
formatter = CustomJsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s',
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


# <-- NUOVO: Funzione eseguita prima di ogni richiesta -->
@app.before_request
def add_request_id():
    """Cattura il request ID dall'header o ne genera uno nuovo."""
    # Cerca l'header X-Request-ID (case-insensitive)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        # Se non c'è, ne crea uno nuovo
        request_id = str(uuid.uuid4())
    # Memorizza l'ID nell'oggetto 'g', che vive solo per la durata di questa richiesta
    g.request_id = request_id


# --- Endpoint (il codice degli endpoint non deve cambiare!) ---
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
        app.logger.error(f"Error in /info endpoint: {str(e)}")
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
            app.logger.warning("Il campo 'text' non è una stringa")
            return {"error": "The 'text' field must be a string"}, 400

        anonymized_text_output = anonymize_text_with_presidio(input_text)
        app.logger.info("Anonimizzazione completata con successo")
        return {"text": anonymized_text_output}, 200

    except Exception as e:
        app.logger.error(f"Error in /anonymize endpoint: {str(e)}")
        return {"error": "An internal server error occurred"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)