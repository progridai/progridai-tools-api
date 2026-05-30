import uuid
import time
from typing import Dict, Tuple

# TTL in seconds: 24 hours
TTL_SECONDS = 24 * 60 * 60

# In-memory store: mapId -> (expires_at, token_map)
_store: Dict[str, Tuple[float, Dict[str, str]]] = {}

def create_map(token_map: Dict[str, str]) -> str:
    map_id = uuid.uuid4().hex
    expires_at = time.time() + TTL_SECONDS
    _store[map_id] = (expires_at, token_map)
    return map_id

def get_map(map_id: str) -> Dict[str, str]:
    if map_id not in _store:
        return None
    expires_at, token_map = _store[map_id]
    if time.time() > expires_at:
        del _store[map_id]
        return None
    return token_map

def delete_map(map_id: str) -> bool:
    if map_id in _store:
        del _store[map_id]
        return True
    return False
