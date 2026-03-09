from fastapi.testclient import TestClient

from app.user.application.exceptions.user import UserEmailAlreadyExistsException
from app.user.application.service.user import UserService
from main import create_app


def test_create_user_duplicate_email_returns_400(monkeypatch):
    app = create_app()
    client = TestClient(app)

    async def raise_duplicate_email(*_args, **_kwargs):
        raise UserEmailAlreadyExistsException()

    monkeypatch.setattr(UserService, "create_user", raise_duplicate_email)

    response = client.post(
        "/api/users",
        json={
            "username": "testuser",
            "password": "secure_password123",
            "email": "dup@example.com",
            "nickname": "tester",
            "real_name": "김테스트",
            "phone_number": "010-1234-5678",
        },
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "USER__EMAIL_ALREADY_EXISTS"
