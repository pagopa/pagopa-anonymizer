from flask import Flask, request, jsonify
from configparser import ConfigParser
import os
from src.anonymizer_logic import anonymize_text_with_presidio

app = Flask(__name__)

@app.route('/info', methods=['GET'])
def info():
    """
    GET endpoint for liveness & readiness 
    Returns:
        name: The name of the application
        version: The application version
        environment: The environment variable from .env
    """
    try:
        config = ConfigParser()
        config.read('setup.cfg')
        app_name = config.get("metadata", "name")
        app_version = config.get("metadata", "version")
        return jsonify({"name": app_name, "version": app_version, "environment": os.getenv("ENV", "not specified")}), 200

    except Exception as e:
        # Generic error handling for unexpected issues
        app.logger.error(f"Error in /info endpoint: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/anonymize', methods=['POST'])
def anonymize_endpoint():
    """
    POST endpoint to anonymize the provided text.
    Expects a JSON body with a "text" field.
    """
    try:
        # 1. Get JSON data from the request
        data = request.get_json()

        # 2. Validate that data was sent and 'text' key exists
        if not data:
            return jsonify({"error": "Invalid JSON request or incorrect Content-Type (must be application/json)"}), 400

        input_text = data.get('text')

        if input_text is None:
            return jsonify({"error": "The 'text' field is missing from the JSON request body"}), 400

        if not isinstance(input_text, str):
            return jsonify({"error": "The 'text' field must be a string"}), 400

        # 3. Call the anonymization logic from the separate module
        anonymized_text_output = anonymize_text_with_presidio(input_text)

        # 4. Return the response
        return jsonify({"text": anonymized_text_output}), 200

    except Exception as e:
        # Generic error handling for unexpected issues
        app.logger.error(f"Error in /anonymize endpoint: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # Run the Flask app. debug=True is useful for development.
    app.run(debug=False, port=5000)