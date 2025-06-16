import unittest

from src.anonymizer_logic import anonymize_text_with_presidio

class TestAnonymizerLogic(unittest.TestCase):
    def test_anonymize_success_person(self):
        anonymize_text=anonymize_text_with_presidio('multa a Luca Rossi')
        self.assertEqual(anonymize_text, "multa a L*** R****")
    def test_anonymize_success_address(self):
        test_cases = [
            ("Via", "Indirizzo Via Umberto I n.54, 00184 Roma RM", "Indirizzo Via Umberto I n Roma RM"),
            ("Viale", "Indirizzo Viale Europa 12, 20126 Milano MI", "Indirizzo Viale Europa Milano MI"),
            ("Corso", "Indirizzo Corso Italia 33, 56125 Pisa PI", "Indirizzo Corso Italia Pisa PI"),
            ("Strada", "Indirizzo Strada Statale 45, 43123 Parma PR", "Indirizzo Strada Statale Parma PR"),
            ("Stradone", "Indirizzo Stradone Vecchio 7, 37129 Verona VR", "Indirizzo Stradone Vecchio Verona VR"),
            ("Circonvallazione", "Indirizzo Circonvallazione Sud 101, 40121 Bologna BO", "Indirizzo Circonvallazione Sud Bologna BO"),
            ("Piazzale", "Indirizzo Piazzale Roma 2, 30135 Venezia VE", "Indirizzo Piazzale Roma Venezia VE"),
            ("Piazza", "Indirizzo Piazza Garibaldi 8, 80142 Napoli NA", "Indirizzo Piazza Garibaldi Napoli NA"),
            ("Piazzetta", "Indirizzo Piazzetta San Marco 5, 80132 Napoli NA", "Indirizzo Piazzetta San Marco Napoli NA"),
            ("Largo", "Indirizzo Largo Augusto 10, 20122 Milano MI", "Indirizzo Largo Augusto Milano MI"),
            ("Rotonda", "Indirizzo Rotonda dei Mille 3, 10123 Torino TO", "Indirizzo Rotonda dei Mille Torino TO"),
            ("Vicolo", "Indirizzo Vicolo Stretto 4, 95131 Catania CT", "Indirizzo Vicolo Stretto Catania CT"),
            ("Traversa", "Indirizzo Traversa Nuova 9, 80143 Napoli NA", "Indirizzo Traversa Nuova Napoli NA"),
            ("Rampa", "Indirizzo Rampa della Vittoria 6, 16121 Genova GE", "Indirizzo Rampa della Vittoria Genova GE"),
            ("Salita", "Indirizzo Salita Castello 11, 16123 Genova GE", "Indirizzo Salita Castello Genova GE"),
            ("Discesa", "Indirizzo Discesa Mare 13, 90133 Palermo PA", "Indirizzo Discesa Mare Palermo PA"),
            ("Spalto", "Indirizzo Spalto Marengo 15, 15121 Alessandria AL", "Indirizzo Spalto Marengo Alessandria AL"),
            ("Passeggiata", "Indirizzo Passeggiata Lungomare 18, 17021 Alassio SV", "Indirizzo Passeggiata Lungomare Alassio SV"),
            ("Località", "Indirizzo Località Bosco 21, 52010 Subbiano AR", "Indirizzo Località Bosco Subbiano AR"),
            ("Contrada", "Indirizzo Contrada Colle 23, 66020 San Giovanni CH", "Indirizzo Contrada Colle San Giovanni CH"),
            ("Ruga", "Indirizzo Ruga Rialto 25, 30125 Venezia VE", "Indirizzo Ruga Rialto Venezia VE"),
            ("Rio Terà", "Indirizzo Rio Terà San Leonardo 27, 30121 Venezia VE", "Indirizzo Rio Terà San Leonardo Venezia VE"),
            ("Salizada", "Indirizzo Salizada San Giovanni 29, 30122 Venezia VE", "Indirizzo Salizada San Giovanni Venezia VE"),
            ("Fondamenta", "Indirizzo Fondamenta Nove 31, 30121 Venezia VE", "Indirizzo Fondamenta Nove Venezia VE"),
            ("Calle", "Indirizzo Calle Larga 33, 30124 Venezia VE", "Indirizzo Calle Larga Venezia VE"),
            ("Campo", "Indirizzo Campo Santa Margherita 35, 30123 Venezia VE", "Indirizzo Campo Santa Margherita Venezia VE"),
            ("Sottoportego", "Indirizzo Sottoportego del Forno 37, 30121 Venezia VE", "Indirizzo Sottoportego del Forno Venezia VE"),
            ("Corticella", "Indirizzo Corticella San Marco 39, 40121 Bologna BO", "Indirizzo Corticella San Marco Bologna BO"),
            ("Chiasso", "Indirizzo Chiasso delle Monache 41, 22100 Como CO", "Indirizzo Chiasso delle Monache Como CO"),
            ("Angiporto", "Indirizzo Angiporto Galleria 43, 80132 Napoli NA", "Indirizzo Angiporto Galleria Napoli NA"),
            ("Via", "Indirizzo Via Umberto I n.54 Roma RM", "Indirizzo Via Umberto I n Roma RM"),
            ("Via", "Indirizzo Via Umberto I n.54, 80132 Napoli NA Codice 2030", "Indirizzo Via Umberto I n Napoli NA Codice 2030"),
        ]
        for toponym, input_text, expected in test_cases:
            anonymize_text = anonymize_text_with_presidio(input_text)
            self.assertEqual(
                anonymize_text, expected,
                msg=f"Failed for toponym: {toponym}"
            )

    def test_anonymize_success_vehicle_plate(self):
        anonymize_text=anonymize_text_with_presidio('Macchina HA011HA')
        self.assertEqual(anonymize_text, "Macchina HA0****")
    # def test_anonymize_success_nav(self):
    #     anonymize_text=anonymize_text_with_presidio('000000000000000000')
    #     self.assertEqual(anonymize_text, "<ANONYMIZED>")
    # def test_anonymize_success_iuv(self):
    #     anonymize_text=anonymize_text_with_presidio('00000000000000000')
    #     self.assertEqual(anonymize_text, "<ANONYMIZED>")
    def test_anonymize_success_medical_info(self):
        test_cases = [
            # (patology, input_text, expected_output)
            ("allergologica", "Diagnosi allergologica confermata", "Diagnosi confermata"),
            ("allergologico", "Referto allergologico disponibile", "Referto disponibile"),
            ("ambulatoriale", "Visita ambulatoriale completata", "Visita completata"),
            ("andrologica", "Consulenza andrologica richiesta", "Consulenza richiesta"),
            ("anatomopatologica", "Analisi anatomopatologica in corso", "Analisi in corso"),
            ("audiometrico", "Test audiometrico effettuato", "Test effettuato"),
            ("cardiologica", "Valutazione cardiologica positiva", "Valutazione positiva"),
            ("cardiologico", "Esame cardiologico programmato", "Esame programmato"),
            ("chirurgica", "Intervento di chirurgica urgente", "Intervento di urgente"),
            ("chirurgico", "Trattamento chirurgico eseguito", "Trattamento eseguito"),
            ("citologica", "Indagine citologica negativa", "Indagine negativa"),
            ("citologico", "Referto citologico pronto", "Referto pronto"),
            ("delle feci", "Analisi delle feci completata", "Analisi completata"),
            ("delle urine", "Risultato delle urine disponibile", "Risultato disponibile"),
            ("del sangue", "Prelievo del sangue effettuato", "Prelievo effettuato"),
            ("dermatologica", "Visita dermatologica prenotata", "Visita prenotata"),
            ("dermatologico", "Controllo dermatologico annuale", "Controllo annuale"),
            ("di laboratorio", "Esame di laboratorio richiesto", "Esame richiesto"),
            ("diabetologica", "Valutazione diabetologica in corso", "Valutazione in corso"),
            ("ecografica", "Indagine ecografica programmata", "Indagine programmata"),
            ("ecografico", "Referto ecografico ricevuto", "Referto ricevuto"),
            ("ematologica", "Consulenza ematologica urgente", "Consulenza urgente"),
            ("endocrinologica", "Visita endocrinologica fissata", "Visita fissata"),
            ("endoscopica", "Procedura endoscopica completata", "Procedura completata"),
            ("endoscopico", "Esame endoscopico richiesto", "Esame richiesto"),
            ("estetico", "Trattamento estetico prenotato", "Trattamento prenotato"),
            ("fisioterapica", "Seduta fisioterapica effettuata", "Seduta effettuata"),
            ("geriatrica", "Valutazione geriatrica positiva", "Valutazione positiva"),
            ("gastroenterologica", "Visita gastroenterologica prenotata", "Visita prenotata"),
            ("ginecologica", "Consulenza ginecologica richiesta", "Consulenza richiesta"),
            ("ginecologico", "Controllo ginecologico annuale", "Controllo annuale"),
            ("immunologica", "Analisi immunologica effettuata", "Analisi effettuata"),
            ("immunologico", "Test immunologico negativo", "Test negativo"),
            ("intervento", "Intervento chirurgico programmato", "Intervento programmato"),
            ("istologica", "Diagnosi istologica confermata", "Diagnosi confermata"),
            ("laparoscopico", "Intervento laparoscopico eseguito", "Intervento eseguito"),
            ("logopedica", "Terapia logopedica iniziata", "Terapia iniziata"),
            ("maxillo-facciale", "Chirurgia maxillo-facciale completata", "Chirurgia completata"),
            ("nefrologica", "Valutazione nefrologica richiesta", "Valutazione richiesta"),
            ("nefrologico", "Esame nefrologico programmato", "Esame programmato"),
            ("neonatologica", "Assistenza neonatologica fornita", "Assistenza fornita"),
            ("neurochirurgica", "Operazione neurochirurgica riuscita", "Operazione riuscita"),
            ("neurologica", "Visita neurologica prenotata", "Visita prenotata"),
            ("neurologico", "Esame neurologico effettuato", "Esame effettuato"),
            ("nutrizionistica", "Consulenza nutrizionistica richiesta", "Consulenza richiesta"),
            ("oculistica", "Visita oculistica completata", "Visita completata"),
            ("oculistico", "Controllo oculistico annuale", "Controllo annuale"),
            ("odontoiatrica", "Visita odontoiatrica eseguita", "Visita eseguita"),
            ("odontoiatrico", "Intervento odontoiatrico programmato", "Intervento programmato"),
            ("oncologica", "Terapia oncologica iniziata", "Terapia iniziata"),
            ("oncologico", "Esame oncologico richiesto", "Esame richiesto"),
            ("orl", "Visita orl prenotata", "Visita prenotata"),
            ("ortopedica", "Valutazione ortopedica positiva", "Valutazione positiva"),
            ("ortopedico", "Controllo ortopedico annuale", "Controllo annuale"),
            ("ostetrica", "Assistenza ostetrica fornita", "Assistenza fornita"),
            ("otorinolaringoiatrica", "Visita otorinolaringoiatrica effettuata", "Visita effettuata"),
            ("pediatrica", "Visita pediatrica programmata", "Visita programmata"),
            ("plastico", "Intervento plastico eseguito", "Intervento eseguito"),
            ("pneumologica", "Valutazione pneumologica richiesta", "Valutazione richiesta"),
            ("proctologica", "Visita proctologica prenotata", "Visita prenotata"),
            ("psichiatrica", "Consulenza psichiatrica richiesta", "Consulenza richiesta"),
            ("psicodiagnostico", "Test psicodiagnostico effettuato", "Test effettuato"),
            ("psicologica", "Assistenza psicologica fornita", "Assistenza fornita"),
            ("radiografico", "Esame radiografico programmato", "Esame programmato"),
            ("radiologica", "Indagine radiologica completata", "Indagine completata"),
            ("reumatologica", "Visita reumatologica prenotata", "Visita prenotata"),
            ("riabilitativa", "Terapia riabilitativa iniziata", "Terapia iniziata"),
            ("spirometrico", "Test spirometrico effettuato", "Test effettuato"),
            ("urologica", "Visita urologica prenotata", "Visita prenotata"),
            ("urologico", "Esame urologico programmato", "Esame programmato"),
            ("vascolare", "Valutazione vascolare richiesta", "Valutazione richiesta"),
        ]
        for patology, input_text, expected in test_cases:
            anonymize_text = anonymize_text_with_presidio(input_text)
            self.assertEqual(
                anonymize_text, expected,
                msg=f"Failed for patology: {patology}"
            )
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
        anonymize_text=anonymize_text_with_presidio('90728300816')
        self.assertEqual(anonymize_text, "********816") 
    def test_anonymize_success_crypto(self):
        anonymize_text=anonymize_text_with_presidio('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(anonymize_text, "*******************************fNa") 
        # anonymize_text=anonymize_text_with_presidio('0x71C7656EC7ab88b098defB751B7401B5f6d8976F')
        # self.assertEqual(anonymize_text, "*******************************D88") 
        # anonymize_text=anonymize_text_with_presidio('123456789')
        # self.assertEqual(anonymize_text, "*******************************789") 
    def test_anonymize_mixed(self):
        anonymize_text=anonymize_text_with_presidio(
            "Multa per Mario Rossi il giorno 12/07/2025 alle ore 11:00, codice fiscale GTRQWF12L23B157A e carta identita n. AA00000AA, domiciliato in Piazza San Pietro n. 35, 25020 Roma (RM). Pagato attraverso iban IT47J0990650025128761820997 per autovettura targata XX000XX. Contatti numero telefonico 3313516333 ed email test@pagopa.it. Per assistenza andare sul sito web www.test.it")
        self.maxDiff = None
        self.assertEqual(anonymize_text, "Multa per M**** R**** il giorno 12/07/2025 alle ore 11:00, codice fiscale GTRQWF12******** e carta identita n. AA*****AA, domiciliato in Piazza San Pietro n Roma (RM). Pagato attraverso iban IT47J******************0997 per autovettura targata XX0****. Contatti numero telefonico ******6333 ed email t**t@pagopa.it. Per assistenza andare sul sito web www.test.it") 
if __name__ == '__main__':
    unittest.main()
