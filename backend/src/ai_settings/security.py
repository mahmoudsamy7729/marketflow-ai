from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from src.ai_settings import exceptions
from src.config import settings


class AIKeyEncryptor:
    def __init__(self, encryption_key: str) -> None:
        if not encryption_key:
            raise exceptions.AIEncryptionConfigurationError()
        self.fernet = Fernet(encryption_key.encode("utf-8"))

    def encrypt(self, value: str) -> str:
        try:
            return self.fernet.encrypt(value.encode("utf-8")).decode("utf-8")
        except Exception as exc:
            raise exceptions.AIEncryptionConfigurationError() from exc

    def decrypt(self, value: str) -> str:
        try:
            return self.fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError) as exc:
            raise exceptions.AIEncryptionConfigurationError() from exc


def build_ai_key_encryptor() -> AIKeyEncryptor:
    return AIKeyEncryptor(settings.ai_encryption_key)
