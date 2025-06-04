import unittest

from src.anonymizer_logic import anonymize_text_with_presidio

class TestAnonymizerLogic(unittest.TestCase):
    def test_anonymize_success_person(self):
        anonymize_text=anonymize_text_with_presidio('multa a Mario Rossi')
        self.assertEqual(anonymize_text, "multa a <PERSON>")
    def test_anonymize_success_address(self):
        anonymize_text=anonymize_text_with_presidio('Indirizzo Via umberto I n.54')
        self.assertEqual(anonymize_text, "Indirizzo <ADDRESS>")
    def test_anonymize_success_vehicle_plate(self):
        anonymize_text=anonymize_text_with_presidio('Macchina XX000XX')
        self.assertEqual(anonymize_text, "Macchina <PLATE_NUMBER>")
    def test_anonymize_success_nav(self):
        anonymize_text=anonymize_text_with_presidio('000000000000000000')
        self.assertEqual(anonymize_text, "<ANONYMIZED>")
    def test_anonymize_success_iuv(self):
        anonymize_text=anonymize_text_with_presidio('00000000000000000')
        self.assertEqual(anonymize_text, "<ANONYMIZED>")
    def test_anonymize_success_medical_info(self):
        anonymize_text=anonymize_text_with_presidio('visita medica radiografia')
        self.assertEqual(anonymize_text, "visita medica <MEDICAL_REFERENCE>")
    def test_anonymize_success_email(self):
        anonymize_text=anonymize_text_with_presidio('test@pagopa.it')
        self.assertEqual(anonymize_text, "<EMAIL>")
    def test_anonymize_success_phone_number_separated(self):
        anonymize_text=anonymize_text_with_presidio('331 3516333')
        self.assertEqual(anonymize_text, "<PHONE>")
    def test_anonymize_success_phone_number_united(self):
        anonymize_text=anonymize_text_with_presidio('3313516333')
        self.assertEqual(anonymize_text, "<PHONE>")
    def test_anonymize_success_tax_code(self):
        anonymize_text=anonymize_text_with_presidio('GTRQWF12L23B157A')
        self.assertEqual(anonymize_text, "<FISCAL_CODE>")   
    def test_anonymize_success_iban(self):
        anonymize_text=anonymize_text_with_presidio('IT47J0990650025128761820997')
        self.assertEqual(anonymize_text, "<ANONYMIZED>")    
    def test_anonymize_success_credit_card(self):
        anonymize_text=anonymize_text_with_presidio('4231284493213295')
        self.assertEqual(anonymize_text, "<ANONYMIZED>")       
    def test_anonymize_success_url(self):
        anonymize_text=anonymize_text_with_presidio('test.it')
        self.assertEqual(anonymize_text, "<ANONYMIZED>") 
    def test_anonymize_success_date(self):
        anonymize_text=anonymize_text_with_presidio('12/07/1998 00:00')
        self.assertEqual(anonymize_text, "<ANONYMIZED> 00:00") 
    def test_anonymize_success_identity_card(self):
        anonymize_text=anonymize_text_with_presidio('AA00000AA')
        self.assertEqual(anonymize_text, "<ANONYMIZED>") 
    def test_anonymize_success_passport(self):
        anonymize_text=anonymize_text_with_presidio('AA0000000')
        self.assertEqual(anonymize_text, "<ANONYMIZED>") 
    def test_anonymize_mixed(self):
        anonymize_text=anonymize_text_with_presidio(
            "Multa per Mario Rossi il giorno 12/07/2025 alle ore 11:00, codice fiscale GTRQWF12L23B157A e carta identita n. AA00000AA, domiciliato in Piazza San Pietro n. 35. Pagato attraverso iban IT47J0990650025128761820997 per autovettura targata XX000XX. Contatti numero telefonico 3313516333 ed email test@pagopa.it. Per assistenza andare sul sito web www.test.it")
        self.assertEqual(anonymize_text, "Multa per <PERSON> il giorno <ANONYMIZED> alle ore 11:00, codice fiscale <FISCAL_CODE> e carta identita n. <ANONYMIZED>, domiciliato in <ADDRESS>. Pagato attraverso iban <ANONYMIZED> per autovettura targata <PLATE_NUMBER>. Contatti numero telefonico <PHONE> ed email <EMAIL>. Per assistenza andare sul sito web <ANONYMIZED>") 
if __name__ == '__main__':
    unittest.main()
