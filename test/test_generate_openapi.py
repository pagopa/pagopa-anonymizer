import sys
import os

## Add the directory containing your package to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from src.app import app 

class GenerateOpenapi(unittest.TestCase):
    def test_generate_openapi(self):
        openapi_dict = app.api_doc
        import json
        with open("infra/api/openapi.json", "w") as f:
            json.dump(openapi_dict, f, indent=2)
        print("openapi.json generated successfully.")

if __name__ == '__main__':
    unittest.main()