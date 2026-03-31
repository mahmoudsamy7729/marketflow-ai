from fastapi.security import HTTPBearer

# OAuth2 schema for JWT bearer token authentication
oauth2_schema = HTTPBearer(auto_error=False)

# Alias for backward compatibility
JWTBearer = HTTPBearer

__all__ = ["oauth2_schema", "JWTBearer"]






