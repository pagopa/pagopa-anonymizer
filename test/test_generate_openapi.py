import os
import json
import unittest
from src.app import app
from configparser import ConfigParser


class GenerateOpenapi(unittest.TestCase):
    def test_generate_openapi(self):
        openapi_dict = app.api_doc

        config = ConfigParser()
        config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'setup.cfg')))
        app_version = config.get("metadata", "version")

        if "info" in openapi_dict:
            openapi_dict["info"]["version"] = app_version
        else:
            openapi_dict["info"] = {"version": app_version}

        # Costruisci percorso assoluto rispetto alla directory del file di test
        output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra', 'api', 'v1', 'openapi.json'))

        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Scrivi il file
        with open(output_file, "w") as f:
            json.dump(openapi_dict, f, indent=2)

        print("openapi.json generated successfully.")


if __name__ == '__main__':
    unittest.main()
