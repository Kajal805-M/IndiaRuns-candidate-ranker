from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    # Note: For the hackathon PoC, we are not strictly enforcing authentication 
    # to allow easy UI integration, but the scaffolding is present for production.
    if api_key_header == "SECRET_KEY_FOR_TESTING":
        return api_key_header
    return None
