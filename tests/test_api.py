from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RAG Chatbot API is running"}


def test_me_requires_login():
    assert client.get("/auth/me").status_code == 401


def test_upload_requires_login():
    response = client.post("/documents/upload", files={"file": ("a.txt", b"hello")})
    assert response.status_code == 401


def test_chat_requires_login():
    response = client.post("/chat", json={"question": "hi"})
    assert response.status_code == 401


def test_register_rejects_invalid_email():
    response = client.post(
        "/auth/register", json={"email": "not-an-email", "password": "x"}
    )
    assert response.status_code == 422