import unicodedata
from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine

COMMON_SAFE_TERMS = {
    "oi",
    "olá",
    "ola",
    "bom dia",
    "boa tarde",
    "boa noite",
    "tudo bem",
    "td bem",
    "ok",
    "sim",
    "não",
    "nao",
    "valeu",
    "obrigado",
    "obrigada"
}

CUSTOM_PERSON_NAMES = {
    "Rodrigo",
    "Rodrigo Goulart",
    "Rodrigo Goulart da Rosa",
    "Maurício",
    "Mauricio"
}

rg_pattern = Pattern(
    name="rg_pattern",
    regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]\b",
    score=0.75
)

rg_recognizer = PatternRecognizer(
    supported_entity="RG",
    patterns=[rg_pattern],
    context=[
        "rg",
        "registro geral",
        "registro de identidade",
        "cédula de identidade",
        "cedula de identidade",
        "identidade",
        "documento de identidade"
    ],
    supported_language="pt"
)

custom_person_recognizer = PatternRecognizer(
    supported_entity="PERSON",
    deny_list=list(CUSTOM_PERSON_NAMES),
    supported_language="pt"
)

def register_custom_recognizers(analyzer: AnalyzerEngine):
    analyzer.registry.add_recognizer(rg_recognizer)
    analyzer.registry.add_recognizer(custom_person_recognizer)
    return analyzer

def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text

def is_safe_short_message(text: str) -> bool:
    normalized = normalize_text(text)
    return normalized in COMMON_SAFE_TERMS

def should_ignore_result(text: str, result) -> bool:
    detected_text = text[result.start:result.end]
    normalized_detected = normalize_text(detected_text)
    normalized_full_text = normalize_text(text)

    if normalized_detected in COMMON_SAFE_TERMS:
        return True

    if len(normalized_full_text) <= 10 and result.entity_type in {
        "ORGANIZATION",
        "ESTABELECIMENTO",
        "LOCATION"
    }:
        return True

    if result.entity_type in {"ORGANIZATION", "ESTABELECIMENTO"} and result.score < 0.80:
        return True

    return False
