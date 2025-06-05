from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine, OperatorConfig


# Italian Address Recognizer
# Matches common Italian street address formats.
italian_address_patterns = [
    Pattern(
        name="Address (Type + Name + Number)",
        regex=r"(Via|Viale|Piazza|Corso|Largo|Strada|Contrada|Borgo|Salita|Calata|Passeggiata) +[A-ZÀ-Üa-zà-ü0-9'’\.\-\s]+?,?\s*\d+[A-Za-z]?",
        score=0.9
    ),
]
# Using "ITALIAN_ADDRESS" as entity type to clearly indicate its specificity.
address_recognizer = PatternRecognizer(
    supported_entity="ITALIAN_ADDRESS",
    name="ItalianAddressRecognizer",
    patterns=italian_address_patterns,
    supported_language="it", # This recognizer is for Italian
    context=["indirizzo", "residenza", "sede legale", "via", "piazza", "corso"] # Context words in Italian
)

# Italian Vehicle Plate Recognizer
# Matches various Italian vehicle plate formats.
plate_pattern = Pattern(name="IT_VEHICLE_PLATE_PATTERN",
                        regex=r"\b([A-Za-z]{2} ?\d{3} ?[A-Za-z]{2}|\d{2} ?[A-Za-z]{2} ?\d{2}|[A-Za-z]{2} ?\d{5}|\d{2} ?[A-Za-z]{3} ?\d{2})\b",
                        score=0.8)
plate_recognizer = PatternRecognizer(patterns=[plate_pattern],
                                     supported_entity="IT_VEHICLE_PLATE",
                                     name="ItalianVehiclePlateRecognizer",
                                     supported_language="it") # This recognizer is for Italian

# NAV (Numero Avviso) Recognizer
# Matches a specific 18-digit number format.
nav_pattern = Pattern(name="NAV_PATTERN",
                      regex=r"\b[0-3]\d{17}\b",
                      score=0.85)
nav_recognizer = PatternRecognizer(patterns=[nav_pattern],
                                   supported_entity="NAV",
                                   name="NavRecognizer",
                                   supported_language="it") # This recognizer is for Italian

# IUV (Identificativo Univoco di Versamento - Unique Payment Identifier) Recognizer
# Matches a specific 17-digit number format.
iuv_pattern = Pattern(name="IUV_PATTERN",
                      regex=r"\b\d{17}\b", # Simplified from original, assuming it's exactly 17 digits
                      score=0.8)
iuv_recognizer = PatternRecognizer(patterns=[iuv_pattern],
                                   supported_entity="IUV",
                                   name="IuvRecognizer",
                                   supported_language="it") # This recognizer is for Italian

# Medical Information Recognizer
# This pattern is for Italian "visita medica".
medical_patterns = [
    Pattern(
        name="MEDICAL_MENTION",
        regex=r"\b(?<=visita\s)(.*)$",
        score=0.7
    ),
]
medical_recognizer = PatternRecognizer(
    supported_entity="MEDICAL_INFO", # Generic entity for medical-related information
    name="MedicalInfoRecognizer",
    patterns=medical_patterns,
    supported_language="it", # This recognizer is for Italian
    context=["visita", "medica", "ospedale", "dottore", "cura", "terapia", "diagnosi"] # Context words in Italian
)


# --- Presidio Configuration ---

# 1. NLP Engine (spaCy)
# Ensure you have the Italian model downloaded: python -m spacy download it_core_news_lg
# If you plan to process English text, change "it" to "en" and use an English model like "en_core_web_lg".
NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "it", "model_name": "it_core_news_lg"}]
}
PROVIDER = NlpEngineProvider(nlp_configuration=NLP_CONFIG)
NLP_ENGINE = PROVIDER.create_engine()

# 2. Analyzer Engine
ANALYZER = AnalyzerEngine(
    nlp_engine=NLP_ENGINE,
    supported_languages=["it"] # Specify that the analyzer supports Italian
)
# Add custom recognizers
ANALYZER.registry.add_recognizer(address_recognizer)
ANALYZER.registry.add_recognizer(plate_recognizer)
ANALYZER.registry.add_recognizer(nav_recognizer)
ANALYZER.registry.add_recognizer(iuv_recognizer)
ANALYZER.registry.add_recognizer(medical_recognizer)
# Presidio's default recognizers for "it" will also be active.

# 3. Anonymizer Engine
ANONYMIZER = AnonymizerEngine()

anonymize_keep_initials_lambda = lambda text: " ".join(
    [
        (word[:2] + "*" * (len(word) - 2)) if word else ""
        for word in str(text).split(' ')
    ]
)

# 4. Anonymization Operators
# Defines how recognized PII should be replaced.
DEFAULT_OPERATORS = {
    "DEFAULT": OperatorConfig("custom", {"lambda": anonymize_keep_initials_lambda}),
    "LOCATION": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
    "IT_VEHICLE_PLATE": OperatorConfig("replace", {"new_value": "<IT_VEHICLE_PLATE>"}),
    "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
    # You can define specific operators for different entity types:
    # "PERSON": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "ITALIAN_ADDRESS": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "IT_VEHICLE_PLATE": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "NAV_NUMBER": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "IUV_CODE": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "MEDICAL_INFO": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "EMAIL_ADDRESS": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "PHONE_NUMBER": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
    # "IT_FISCAL_CODE": OperatorConfig("mask", {"chars_to_mask": 3, "masking_char": "*", "from_end": True}),
}

# 5. Entities to target for anonymization
# This list includes Presidio's built-in entities for Italian and your custom ones.
ENTITIES_TO_ANONYMIZE = [
    # Presidio built-in (many are language-agnostic or have 'it' versions)
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD", # Language agnostic
    "IBAN_CODE",   # Language agnostic, but format can be country specific
    "URL",         # Language agnostic
    "DATE_TIME",   # Language agnostic but recognizes formats common in the language
    "CRYPTO",      # Language agnostic
    "NRP",         # National Registration P. (general, may need specific IT)
    #"LOCATION",

    # Presidio Italian-specific built-in
    "IT_FISCAL_CODE",
    "IT_VAT_NUMBER", # Presidio uses IT_VAT_NUMBER
    "IT_DRIVER_LICENSE",
    "IT_PASSPORT",
    "IT_IDENTITY_CARD",

    # custom entities (ensure names match `supported_entity` in recognizers)
    "ITALIAN_ADDRESS",
    "IT_VEHICLE_PLATE",
    "NAV",
    "IUV",
    "MEDICAL_INFO"
]


def anonymize_text_with_presidio(text_to_anonymize: str) -> str:
    """
    Anonymizes the input text using the configured Presidio Analyzer and Anonymizer.
    The current configuration is primarily for Italian text.
    """
    try:
        analyzer_results = ANALYZER.analyze(
            text=text_to_anonymize,
            entities=ENTITIES_TO_ANONYMIZE,
            language="it" # Crucial to specify the language of the text
        )
        anonymized_result = ANONYMIZER.anonymize(
            text=text_to_anonymize,
            analyzer_results=analyzer_results,
            operators=DEFAULT_OPERATORS
        )
        return anonymized_result.text
    except Exception as e:
        # In a real application, you would use proper logging
        print(f"Error during Presidio anonymization: {e}")
        # Decide on fallback behavior: return original text, or an error message
        return f"Error during anonymization: {text_to_anonymize}"

