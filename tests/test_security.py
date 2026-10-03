import jwt

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("test123")
    assert hashed != "test123"
    assert verify_password("test123", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_contains_subject():
    token = create_access_token("user-123")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "user-123"