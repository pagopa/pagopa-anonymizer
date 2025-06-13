import unittest

from src.anonymizer_logic import anonymize_text_with_presidio

class TestAnonymizerLogic(unittest.TestCase):
    def test_anonymize_success_person(self):
        anonymize_text=anonymize_text_with_presidio('multa a Luca Rossi')
        self.assertEqual(anonymize_text, "multa a L*** R****")
    def test_anonymize_success_address(self):
        anonymize_text=anonymize_text_with_presidio('Indirizzo Via umberto I n.54')
        self.assertEqual(anonymize_text, "Indirizzo Via umberto I n")
    def test_anonymize_success_vehicle_plate(self):
        anonymize_text=anonymize_text_with_presidio('Macchina HA011HA')
        self.assertEqual(anonymize_text, "Macchina HA0****")
    def test_anonymize_success_nav(self):
        anonymize_text=anonymize_text_with_presidio('000000000000000000')
        self.assertEqual(anonymize_text, "<ANONYMIZED>")
    def test_anonymize_success_iuv(self):
        anonymize_text=anonymize_text_with_presidio('00000000000000000')
        self.assertEqual(anonymize_text, "<ANONYMIZED>")
    def test_anonymize_success_medical_info(self):
        anonymize_text=anonymize_text_with_presidio('visita medica radiografia')
        self.assertEqual(anonymize_text, "visita <MEDICAL_REFERENCE>") # TODO
    def test_anonymize_success_email(self):
        anonymize_text=anonymize_text_with_presidio('lucarossi@pagopa.it')
        self.assertEqual(anonymize_text, "l*******i@pagopa.it")
        anonymize_text=anonymize_text_with_presidio('luca.rossi@pagopa.it')
        self.assertEqual(anonymize_text, "l********i@pagopa.it")
    def test_anonymize_success_phone_number_separated(self):
        anonymize_text=anonymize_text_with_presidio('3485536559')
        self.assertEqual(anonymize_text, "******6559")
        anonymize_text=anonymize_text_with_presidio('348 5536559')
        self.assertEqual(anonymize_text, "******6559")
        anonymize_text=anonymize_text_with_presidio('+393485536559')
        self.assertEqual(anonymize_text, "*********6559")
        anonymize_text=anonymize_text_with_presidio('+39 3485536559')
        self.assertEqual(anonymize_text, "*********6559")
        anonymize_text=anonymize_text_with_presidio('+39348 5536559')
        self.assertEqual(anonymize_text, "*********6559")
    def test_anonymize_success_tax_code(self):
        anonymize_text=anonymize_text_with_presidio('RSSLCU80A01F205I')
        self.assertEqual(anonymize_text, "RSSLCU80********")   
    def test_anonymize_success_iban(self):
        anonymize_text=anonymize_text_with_presidio('IT47J0990650025128761820997')
        self.assertEqual(anonymize_text, "IT47J******************0997")    
    def test_anonymize_success_credit_card(self):
        anonymize_text=anonymize_text_with_presidio('4012 8888 8888 1881')
        self.assertEqual(anonymize_text, "**** **** **** 1881")       
        anonymize_text=anonymize_text_with_presidio('4012888888881881')
        self.assertEqual(anonymize_text, "************1881")       
    # def test_anonymize_success_url(self):
    #     anonymize_text=anonymize_text_with_presidio('test.it')
    #     self.assertEqual(anonymize_text, "<ANONYMIZED>") 
    # def test_anonymize_success_date(self):
    #     anonymize_text=anonymize_text_with_presidio('12/07/1998 00:00')
    #     self.assertEqual(anonymize_text, "<ANONYMIZED> 00:00") 
    def test_anonymize_success_identity_card_paper(self):
        anonymize_text=anonymize_text_with_presidio('AH9013703')
        self.assertEqual(anonymize_text, "AH*****03") 
    def test_anonymize_success_identity_card_cie(self):
        anonymize_text=anonymize_text_with_presidio('CA12345AB')
        self.assertEqual(anonymize_text, "CA*****AB") 
    def test_anonymize_success_passport(self):
        anonymize_text=anonymize_text_with_presidio('KK5004513')
        self.assertEqual(anonymize_text, "KK*****13") 
    def test_anonymize_success_driver_license(self):
        anonymize_text=anonymize_text_with_presidio('RO5157033P')
        self.assertEqual(anonymize_text, "RO******3P") 
    def test_anonymize_success_vat_code(self):
        anonymize_text=anonymize_text_with_presidio('12345678967')
        self.assertEqual(anonymize_text, "********967") 
    def test_anonymize_success_crypto(self):
        anonymize_text=anonymize_text_with_presidio('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(anonymize_text, "*******************************fNa") 
        anonymize_text=anonymize_text_with_presidio('0x32Be343B94f860124dC4fEe278FDCBD38C102D88')
        self.assertEqual(anonymize_text, "*******************************fNa") 
        anonymize_text=anonymize_text_with_presidio('123456789')
        self.assertEqual(anonymize_text, "*******************************fNa") 
    def test_anonymize_mixed(self):
        anonymize_text=anonymize_text_with_presidio(
            "Multa per Mario Rossi il giorno 12/07/2025 alle ore 11:00, codice fiscale GTRQWF12L23B157A e carta identita n. AA00000AA, domiciliato in Piazza San Pietro n. 35. Pagato attraverso iban IT47J0990650025128761820997 per autovettura targata XX000XX. Contatti numero telefonico 3313516333 ed email test@pagopa.it. Per assistenza andare sul sito web www.test.it")
        self.maxDiff = None
        self.assertEqual(anonymize_text, "Multa per M**** R**** il giorno 12/07/2025 alle ore 11:00, codice fiscale GTRQWF12******** e carta identita n. AA*****AA, domiciliato in Piazza San Pietro n . Pagato attraverso iban IT47J******************0997 per autovettura targata XX0****. Contatti numero telefonico ******6333 ed email t**t@pagopa.it. Per assistenza andare sul sito web www.test.it") 
if __name__ == '__main__':
    unittest.main()
