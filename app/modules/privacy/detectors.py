from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult
from typing import List
from app.modules.privacy.validators import validate_cpf, validate_cnpj

class CPFRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                "CPF Pattern",
                r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
                0.5
            )
        ]
        super().__init__(
            supported_entity="CPF",
            patterns=patterns,
            context=["cpf", "cadastro de pessoa física"],
            supported_language="pt",
        )

    def validate_result(self, pattern_text: str) -> bool:
        return validate_cpf(pattern_text)

class CNPJRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                "CNPJ Pattern",
                r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
                0.5
            )
        ]
        super().__init__(
            supported_entity="CNPJ",
            patterns=patterns,
            context=["cnpj", "cadastro nacional de pessoa jurídica"],
            supported_language="pt",
        )

    def validate_result(self, pattern_text: str) -> bool:
        return validate_cnpj(pattern_text)

def add_custom_recognizers(analyzer):
    analyzer.registry.add_recognizer(CPFRecognizer())
    analyzer.registry.add_recognizer(CNPJRecognizer())
