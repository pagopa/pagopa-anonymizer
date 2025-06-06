import sys
import os

## Add the directory containing your package to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from unittest.mock import patch, MagicMock
import unittest
import os
from src.app import app

INFO_ENDPOINT = "/info"
ANONYMIZE_ENDPOINT = "/anonymize"
APP_NAME = "testapp"
APP_VERSION = "testversion"
ENVIRONMENT = "test"
TEXT_TO_ANONYM = "text"

class TestInfoEndpoint(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch("src.app.ConfigParser")
    def test_info_success(self, mock_config_parser):
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key: {"name": APP_NAME, "version": APP_VERSION}[key]
        mock_config_parser.return_value = mock_config
        os.environ["ENV"] = ENVIRONMENT
        response = self.client.get(INFO_ENDPOINT)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], APP_NAME)
        self.assertEqual(data["version"], APP_VERSION)
        self.assertEqual(data["environment"], ENVIRONMENT)
        del os.environ["ENV"]

    @patch("src.app.ConfigParser")
    def test_info_missing_metadata_section(self, mock_config_parser):
        mock_config = MagicMock()
        def raise_no_section(section, key):
            raise Exception("No section: 'metadata'")
        mock_config.get.side_effect = raise_no_section
        mock_config_parser.return_value = mock_config
        response = self.client.get(INFO_ENDPOINT)
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("src.app.ConfigParser")
    def test_info_missing_name_key(self, mock_config_parser):
        mock_config = MagicMock()
        def raise_no_option(section, key):
            if key == "name":
                raise Exception("No option 'name' in section: 'metadata'")
            return APP_VERSION
        mock_config.get.side_effect = raise_no_option
        mock_config_parser.return_value = mock_config
        response = self.client.get(INFO_ENDPOINT)
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("src.app.ConfigParser")
    def test_info_missing_version_key(self, mock_config_parser):
        mock_config = MagicMock()
        def raise_no_option(section, key):
            if key == "version":
                raise Exception("No option 'version' in section: 'metadata'")
            return APP_NAME
        mock_config.get.side_effect = raise_no_option
        mock_config_parser.return_value = mock_config
        response = self.client.get(INFO_ENDPOINT)
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("src.app.ConfigParser")
    def test_info_config_read_raises(self, mock_config_parser):
        mock_config = MagicMock()
        def raise_read(*args, **kwargs):
            raise Exception("Read failed")
        mock_config.read.side_effect = raise_read
        mock_config.get.side_effect = lambda section, key: "dummy"
        mock_config_parser.return_value = mock_config
        response = self.client.get(INFO_ENDPOINT)
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

class TestAnonymizeEndpoint(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch("src.app.anonymize_text_with_presidio")
    def test_anonymize_success(self, mock_config_anonymizer):
        mock_config_anonymizer.return_value = TEXT_TO_ANONYM
        response = self.client.post(ANONYMIZE_ENDPOINT, json={"text": TEXT_TO_ANONYM})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["text"], TEXT_TO_ANONYM)
    
    def test_anonymize_error_invalid_content_type(self):
        response = self.client.post(ANONYMIZE_ENDPOINT, json=False)
        self.assertEqual(response.status_code, 400)

    def test_anonymize_error_text_missing_from_body(self):
        response = self.client.post(ANONYMIZE_ENDPOINT, json={"text": None})
        self.assertEqual(response.status_code, 400)

    def test_anonymize_error_text_invalid_type(self):
        response = self.client.post(ANONYMIZE_ENDPOINT, json={"text": 2})
        self.assertEqual(response.status_code, 400)

    @patch("src.app.anonymize_text_with_presidio")
    def test_anonymize_error_anonymization(self, mock_config_anonymizer):
        mock_config_anonymizer.side_effect = Exception('Read failed')
        response = self.client.post(ANONYMIZE_ENDPOINT, json={"text": TEXT_TO_ANONYM})
        self.assertEqual(response.status_code, 500)

if __name__ == "__main__":
    unittest.main()