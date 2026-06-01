"""Password hashing (bcrypt direct — no passlib)."""
from app.security import hash_password, verify_password


def test_hash_and_verify_roundtrip():
    hashed = hash_password("password123")
    assert hashed.startswith("$2b$")
    assert verify_password("password123", hashed)
    assert not verify_password("wrong", hashed)


def test_verify_rejects_empty():
    assert not verify_password("", "$2b$00test")
    assert not verify_password("x", "")
