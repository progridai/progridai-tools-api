from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from app.modules.privacy.detectors import add_custom_recognizers
from app.modules.privacy.token_store import create_map, get_map
from app.modules.privacy.schemas import (
    SanitizeRequest, SanitizeResponse, EntityOut,
    DetectRequest, DetectResponse,
    ValidateRequest, ValidateResponse,
    RestoreRequest, RestoreResponse
)
from app.modules.privacy.custom_pii_rules import (
    register_custom_recognizers,
    is_safe_short_message,
    should_ignore_result,
    COMMON_SAFE_TERMS
)
from app.shared.exceptions import MapNotFoundException
import re

# Initialize engines
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "pt", "model_name": "pt_core_news_lg"}],
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["pt"])
add_custom_recognizers(analyzer)
register_custom_recognizers(analyzer)
anonymizer = AnonymizerEngine()

# Entities we want to detect based on the requirements
ENTITIES_TO_DETECT = [
    "PERSON",
    "LOCATION",
    "ORGANIZATION",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CPF",
    "CNPJ",
    "RG"
]

MIN_ENTITY_SCORE = {
    "PERSON": 0.85,
    "LOCATION": 0.85,
    "ORGANIZATION": 0.85,
    "RG": 0.80
}

def _map_entity_type(entity_type: str) -> str:
    # Map presidio types to our custom simpler types
    mapping = {
        "EMAIL_ADDRESS": "EMAIL",
        "PHONE_NUMBER": "PHONE"
    }
    return mapping.get(entity_type, entity_type)

class PrivacyService:
    @staticmethod
    def _resolve_overlaps(results: list) -> list:
        priority_map = {
            "CPF": 70,
            "CNPJ": 60,
            "EMAIL": 50,
            "PHONE": 40,
            "RG": 35,
            "PERSON": 30,
            "ORGANIZATION": 20,
            "LOCATION": 10
        }

        def get_priority(ent):
            mapped_type = _map_entity_type(ent.entity_type)
            prio = priority_map.get(mapped_type, 0)
            length = ent.end - ent.start
            score = ent.score
            return (prio, length, score)

        results_sorted_by_prio = sorted(results, key=get_priority, reverse=True)

        chosen_results = []
        for res in results_sorted_by_prio:
            overlap = False
            for chosen in chosen_results:
                if max(res.start, chosen.start) < min(res.end, chosen.end):
                    overlap = True
                    break
            if not overlap:
                chosen_results.append(res)
        return chosen_results

    @staticmethod
    def _filter_real_entities(text: str, results: list) -> list:
        token_pattern = re.compile(r"\[[A-Z]+_\d+\]")
        token_matches = list(token_pattern.finditer(text))
        
        filtered_results = []
        for res in results:
            overlap = False
            for match in token_matches:
                if max(res.start, match.start()) < min(res.end, match.end()):
                    overlap = True
                    break
            
            if not overlap:
                filtered_results.append(res)
                
        return filtered_results

    @staticmethod
    def _filter_by_score(results: list) -> list:
        filtered = []
        for res in results:
            mapped_type = _map_entity_type(res.entity_type)
            if mapped_type in ["CPF", "CNPJ", "EMAIL", "PHONE"]:
                filtered.append(res)
                continue
                
            min_score = MIN_ENTITY_SCORE.get(mapped_type, 0.0)
            if res.score >= min_score:
                filtered.append(res)
        return filtered

    @staticmethod
    def detect(request: DetectRequest) -> DetectResponse:
        if is_safe_short_message(request.text):
            return DetectResponse(hasSensitiveData=False, entities=[])

        results = analyzer.analyze(
            text=request.text,
            entities=ENTITIES_TO_DETECT,
            language="pt",
            allow_list=list(COMMON_SAFE_TERMS)
        )
        
        results = [r for r in results if not should_ignore_result(request.text, r)]
        results = PrivacyService._filter_by_score(results)
        results = PrivacyService._resolve_overlaps(results)
        
        entities = []
        for res in results:
            entities.append(EntityOut(
                type=_map_entity_type(res.entity_type),
                value=request.text[res.start:res.end] if request.includeValues else None,
                start=res.start,
                end=res.end,
                score=res.score
            ))
            
        return DetectResponse(
            hasSensitiveData=len(entities) > 0,
            entities=entities
        )

    @staticmethod
    def sanitize(request: SanitizeRequest) -> SanitizeResponse:
        if is_safe_short_message(request.text):
            return SanitizeResponse(
                sanitizedText=request.text,
                blocked=False,
                entities=[]
            )

        results = analyzer.analyze(
            text=request.text,
            entities=ENTITIES_TO_DETECT,
            language="pt",
            allow_list=list(COMMON_SAFE_TERMS)
        )

        results = [r for r in results if not should_ignore_result(request.text, r)]
        results = PrivacyService._filter_by_score(results)

        if not results:
            return SanitizeResponse(
                sanitizedText=request.text,
                blocked=False,
                entities=[]
            )

        chosen_results = PrivacyService._resolve_overlaps(results)

        # Sort results by start position ascending to assign tokens left-to-right
        results_sorted_asc = sorted(chosen_results, key=lambda x: x.start)
        
        value_to_token = {}
        type_counters = {}
        token_map_internal = {}
        entities_out = []
        
        for res in results_sorted_asc:
            original_value = request.text[res.start:res.end]
            mapped_type = _map_entity_type(res.entity_type)
            key = (mapped_type, original_value)
            if key not in value_to_token:
                type_counters[mapped_type] = type_counters.get(mapped_type, 0) + 1
                token = f"[{mapped_type}_{type_counters[mapped_type]}]"
                value_to_token[key] = token
                token_map_internal[token] = original_value
                entities_out.append(EntityOut(
                    type=mapped_type,
                    token=token
                ))

        # Now sort by start descending to replace in text from end to start
        results_sorted_desc = sorted(chosen_results, key=lambda x: x.start, reverse=True)
        sanitized_text = request.text

        for res in results_sorted_desc:
            original_value = request.text[res.start:res.end]
            mapped_type = _map_entity_type(res.entity_type)
            token = value_to_token[(mapped_type, original_value)]
            
            # Replace in text
            sanitized_text = sanitized_text[:res.start] + token + sanitized_text[res.end:]

        # Validate if still has sensitive data
        token_pattern = re.compile(r"\[[A-Z]+_\d+\]")
        masked_text = token_pattern.sub(lambda m: ' ' * len(m.group(0)), sanitized_text)
        
        validation_results = analyzer.analyze(
            text=masked_text,
            entities=ENTITIES_TO_DETECT,
            language="pt",
            allow_list=list(COMMON_SAFE_TERMS)
        )
        
        validation_results = [r for r in validation_results if not should_ignore_result(masked_text, r)]
        validation_results = PrivacyService._filter_by_score(validation_results)
        validation_results = PrivacyService._filter_real_entities(sanitized_text, validation_results)
        blocked = len(validation_results) > 0

        map_id = None
        if request.restoreEnabled:
            map_id = create_map(token_map_internal)

        return SanitizeResponse(
            sanitizedText=sanitized_text,
            mapId=map_id,
            blocked=blocked,
            entities=entities_out
        )

    @staticmethod
    def restore(request: RestoreRequest) -> RestoreResponse:
        token_map = get_map(request.mapId)
        if token_map is None:
            raise MapNotFoundException()
        
        restored_text = request.text
        # Sort tokens by length descending to avoid partial replacements if there are e.g. [PERSON_1] and [PERSON_10]
        for token, value in sorted(token_map.items(), key=lambda x: len(x[0]), reverse=True):
            restored_text = restored_text.replace(token, value)
            
        return RestoreResponse(restoredText=restored_text)

    @staticmethod
    def validate(request: ValidateRequest) -> ValidateResponse:
        if is_safe_short_message(request.text):
            return ValidateResponse(
                valid=True,
                blocked=False,
                message="Nenhum dado sensível real detectado."
            )

        token_pattern = re.compile(r"\[[A-Z]+_\d+\]")
        masked_text = token_pattern.sub(lambda m: ' ' * len(m.group(0)), request.text)
        
        results = analyzer.analyze(
            text=masked_text,
            entities=ENTITIES_TO_DETECT,
            language="pt",
            allow_list=list(COMMON_SAFE_TERMS)
        )
        
        results = [r for r in results if not should_ignore_result(masked_text, r)]
        results = PrivacyService._filter_by_score(results)
        results = PrivacyService._resolve_overlaps(results)
        results = PrivacyService._filter_real_entities(request.text, results)
        
        if not results:
            return ValidateResponse(
                valid=True,
                blocked=False,
                message="Nenhum dado sensível real detectado."
            )
            
        entities = []
        for res in results:
            entities.append(EntityOut(
                type=_map_entity_type(res.entity_type),
                start=res.start,
                end=res.end
            ))
            
        return ValidateResponse(
            valid=False,
            blocked=True,
            message="Ainda foram encontrados dados sensíveis no texto.",
            entities=entities
        )
