# PII Anonymization Service

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=pagopa_pagopa-anonymizer&metric=alert_status)](https://sonarcloud.io/dashboard?id=pagopa_pagopa-anonymizer)

This project is a simple Flask API that exposes an endpoint to anonymize text, with a particular focus on identifying and masking Personally Identifiable Information (PII) in Italian text using Microsoft Presidio.


<!-- Placeholder for badges - You might consider adding badges for:
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-2.x-orange.svg)](https://flask.palletsprojects.com/)
[![Presidio Version](https://img.shields.io/badge/presidio-latest-green.svg)](https://microsoft.github.io/presidio/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<!-- For CI, if you set up GitHub Actions for linting/testing:
[![CI Pipeline](https://github.com/<YOUR_GITHUB_USER>/<YOUR_REPO_NAME>/actions/workflows/ci.yml/badge.svg)](https://github.com/<YOUR_GITHUB_USER>/<YOUR_REPO_NAME>/actions/workflows/ci.yml)
-->

<!-- TODO: Generate a Table of Contents using a tool like https://ecotrust-canada.github.io/markdown-toc/ after finalizing content -->

<!-- TODO: Resolve all other TODOs in this template -->

---

## API Documentation 📖

This service exposes a single `POST` endpoint: `/anonymize`.

**Request:**
*   Method: `POST`
*   Path: `/anonymize`
*   Headers: `Content-Type: application/json`
*   Body:
    ```json
    {
      "text": "String containing the text to be anonymized."
    }
    ```

**Successful Response (200 OK):**
*   Headers: `Content-Type: application/json`
*   Body:
    ```json
    {
      "text": "String containing the anonymized text."
    }
    ```

**Error Responses:**
*   `400 Bad Request`: Invalid JSON or missing `text` field.
*   `500 Internal Server Error`: Internal processing error.

<!-- TODO: If you decide to generate an OpenAPI/Swagger spec, link it here.
     You can manually create one or use tools if your framework supports it.
     For a simple Flask app like this, the above description might suffice.
See an example of how you might document this with OpenAPI 3:
[OpenAPI 3 Specification (Example)](./openapi/openapi.json)
(You would need to create this openapi.json file)
-->

---

## Technology Stack 🛠️

*   **Python 3.8+**
*   **Flask:** Micro web framework for creating the API.
*   **Presidio Analyzer:** For PII detection.
*   **Presidio Anonymizer:** For PII anonymization/masking.
*   **spaCy:** NLP library used by Presidio for entity recognition (specifically with the Italian model `it_core_news_lg`).
<!-- TODO: Add any other significant libraries or tools used (e.g., Gunicorn for production) -->

---

## Start Project Locally 🚀

### Prerequisites

*   Python 3.8+ and `pip`
*   `git` (for cloning)

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<YOUR_GITHUB_USER>/<YOUR_REPO_NAME>.git
    cd <YOUR_REPO_NAME>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
<!-- No longer needed, it_core_news_lg is in requirements.txt
4.  **Download spaCy Italian language model:**
    ```bash
    python3 -m spacy download it_core_news_lg
    ```
-->

### Run the Application

Start the Flask development server:
```bash
python3 app.py
```
The application will typically be available at `http://127.0.0.1:3000/`.

<!--
TODO: If you create a Docker setup:

### Run with Docker (Optional)

Prerequisites:
- Docker

From the project root directory:
```bash
# 1. Build the Docker image (if you have a Dockerfile)
# docker build -t pii-anonymizer-service .

# 2. Run the Docker container
# docker run -p 5000:5000 pii-anonymizer-service
```
-->

---

## Development 💻

### Project Structure

*   `app.py`: Flask application entry point, API endpoint definition.
*   `presidio_logic.py`: Core Presidio setup, custom recognizers, and anonymization functions.
*   `requirements.txt`: Python dependencies.
*   `venv/`: Virtual environment directory (usually gitignored).
*   `README.md`: This file.
<!-- *   `Dockerfile` (Optional): For containerizing the application. -->
<!-- *   `.github/workflows/` (Optional): For GitHub Actions CI/CD. -->

### Local Development Server

As described in "Run the Application" above:
```bash
python app.py
```

### Python Version Management
It's recommended to use a virtual environment (`venv`) to manage Python versions and dependencies per project. Tools like `pyenv` can also be used for managing multiple Python installations.

---

## Testing 🧪

### Unit Testing (Conceptual)

While this template doesn't include specific unit tests, you would typically use a framework like `pytest` or Python's built-in `unittest` module.

**To run unit tests (example using pytest):**
1.  Install pytest: `pip install pytest`
2.  Create test files (e.g., `test_presidio_logic.py`, `test_app.py`) in a `tests/` directory.
3.  Run tests:
    ```bash
    pytest
    ```
<!-- TODO: Add actual unit tests and update this section. -->

### Manual API Testing

Use tools like `curl`, Postman, or Insomnia to send `POST` requests to the `/anonymize` endpoint.

**Example using `curl`:**
```bash
curl -X POST \
  http://127.0.0.1:3000/anonymize \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Il signor Mario Rossi vive in Via Roma 123. Contattare a mario.rossi@example.com"
  }'
```

<!--
### Integration Testing (Conceptual)

For this service, integration testing might involve setting up the Flask app and sending real HTTP requests to verify the end-to-end anonymization process.
TODO: If you implement automated integration tests (e.g., using `pytest` with HTTP clients, or a separate test suite), describe how to run them.
-->

<!--
### Performance Testing (Conceptual)

Tools like `k6`, `locust`, or `Apache JMeter` can be used for performance testing.
TODO: If you set up performance tests, provide instructions here. Example using k6:
1. Install k6.
2. Create a k6 script (e.g., `performance-test.js`).
3. Run: `k6 run performance-test.js`
-->
