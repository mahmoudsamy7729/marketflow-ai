from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppException(Exception):
    """Base app exception (domain-level)."""
    code: str
    message: str
    status_code: int = 400
    extra: Optional[dict[str, Any]] = None








