from flask import jsonify
from flask_openapi3 import OpenAPI, Info, Tag
from pydantic import BaseModel, Field
from configparser import ConfigParser
import os
from anonymizer_logic import anonymize_text_with_presidio

# OpenAPI metadata
info = Info(title="Anonymizer API", version="1.0.0")
app = OpenAPI(__name__, info=info)

info_tag = Tag(name="Info", description="Liveness & readiness endpoints")
anonymize_tag = Tag(name="Anonymize", description="Text anonymization endpoints")

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

class ValidationErrorModel(BaseModel):
    error: str

@app.get(
    '/info',
    tags=[info_tag],
    responses={
        200: InfoResponse,
        500: ErrorResponse,
    },
    summary="Get application info",
    description="Liveness & readiness endpoint. Returns application name, version, and environment."
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
        return jsonify({"name": app_name, "version": app_version, "environment": os.getenv("ENV", "not specified")}), 200

    except Exception as e:
        app.logger.error(f"Error in /info endpoint: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500

@app.post(
    '/anonymize',
    tags=[anonymize_tag],
    responses={
        200: AnonymizeResponse,
        400: ErrorResponse,
        422: ValidationErrorModel,
        500: ErrorResponse,
    },
    summary="Anonymize text",
    description="Anonymizes the provided text using Presidio.",
    security = [
        {"apiKey": ["write:pets", "read:pets"]}
    ],
)
def anonymize_endpoint(body: AnonymizeRequest):
    """
    POST endpoint to anonymize the provided text.
    """
    try:
        input_text = body.text

        if not isinstance(input_text, str):
            return jsonify({"error": "The 'text' field must be a string"}), 400

        anonymized_text_output = anonymize_text_with_presidio(input_text)
        return jsonify({"text": anonymized_text_output}), 200

    except Exception as e:
        app.logger.error(f"Error in /anonymize endpoint: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)