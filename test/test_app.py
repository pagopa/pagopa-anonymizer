from unittest.mock import patch, MagicMock
import unittest
import os
from src.app import app

class TestInfoController(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch("src.app.ConfigParser")
    def test_info_success(self, mock_config_parser):
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key: {"name": "myapp", "version": "1.2.3"}[key]
        mock_config_parser.return_value = mock_config
        os.environ["ENV"] = "test"
        response = self.client.get('/info')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "myapp")
        self.assertEqual(data["version"], "1.2.3")
        self.assertEqual(data["environment"], "test")
        del os.environ["ENV"]

    @patch("src.app.ConfigParser")
    def test_info_missing_metadata_section(self, mock_config_parser):
        mock_config = MagicMock()
        def raise_no_section(section, key):
            raise Exception("No section: 'metadata'")
        mock_config.get.side_effect = raise_no_section
        mock_config_parser.return_value = mock_config
        response = self.client.get('/info')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("src.app.ConfigParser")
    def test_info_missing_name_key(self, mock_config_parser):
        mock_config = MagicMock()
        def raise_no_option(section, key):
            if key == "name":
                raise Exception("No option 'name' in section: 'metadata'")
            return "1.2.3"
        mock_config.get.side_effect = raise_no_option
        mock_config_parser.return_value = mock_config
        response = self.client.get('/info')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("src.app.ConfigParser")
    def test_info_missing_version_key(self, mock_config_parser):
        mock_config = MagicMock()
        def raise_no_option(section, key):
            if key == "version":
                raise Exception("No option 'version' in section: 'metadata'")
            return "myapp"
        mock_config.get.side_effect = raise_no_option
        mock_config_parser.return_value = mock_config
        response = self.client.get('/info')
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
        response = self.client.get('/info')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()