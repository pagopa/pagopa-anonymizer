import unittest

from src.anonymizer_logic import anonymize_text_with_presidio


class AnonymizerTestCase(unittest.TestCase):
    def test_something(self):
        anonymize_text=anonymize_text_with_presidio('multa a Mario Rossi')
        self.assertEqual(anonymize_text, "multa a <PERSON>")  # add assertion here


if __name__ == '__main__':
    unittest.main()
