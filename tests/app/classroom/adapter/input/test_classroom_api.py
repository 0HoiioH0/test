from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.classroom.application.exception import (
    ClassroomAlreadyExistsException,
    ClassroomNotFoundException,
)
from app.classroom.application.service import ClassroomService
from app.classroom.domain.entity import Classroom
from app.user.adapter.output.persistence.sqlalchemy import (
    UserSQLAlchemyRepository,
)
from app.user.domain.entity import User, UserRole
from core.config import config
from core.domain.types import TokenType
from core.helpers.token import TokenHelper
from main import create_app

ORG_ID = UUID("11111111-1111-1111-1111-111111111111")
PROFESSOR_ID = UUID("22222222-2222-2222-2222-222222222222")
STUDENT_ID = UUID("33333333-3333-3333-3333-333333333333")
OTHER_PROFESSOR_ID = UUID("44444444-4444-4444-4444-444444444444")
ADMIN_ID = UUID("55555555-5555-5555-5555-555555555555")
OTHER_ORG_ID = UUID("99999999-9999-9999-9999-999999999999")


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def make_classroom(
    *,
    professor_ids: list[UUID] | None = None,
    student_ids: list[UUID] | None = None,
) -> Classroom:
    classroom = Classroom(
        organization_id=ORG_ID,
        name="AI 기초",
        professor_ids=professor_ids or [PROFESSOR_ID],
        grade=3,
        semester="1학기",
        section="01",
        description="AI 입문 강의실",
        student_ids=student_ids or [STUDENT_ID],
    )
    classroom.id = UUID("66666666-6666-6666-6666-666666666666")
    return classroom


def make_user(
    *,
    role: UserRole = UserRole.STUDENT,
    user_id: UUID = STUDENT_ID,
    organization_id: UUID = ORG_ID,
) -> User:
    user = User(
        organization_id=organization_id,
        login_id="user01",
        role=role,
        email="user@example.com",
        name="사용자",
    )
    user.id = user_id
    return user


def set_access_token_cookie(client: TestClient, user: User) -> None:
    access_token = TokenHelper.create_token(
        payload={"sub": str(user.id)},
        token_type=TokenType.ACCESS,
    )
    client.cookies.set(config.ACCESS_TOKEN_COOKIE_NAME, access_token)


def test_list_classrooms_returns_only_accessible_classrooms(
    client, monkeypatch
):
    async def list_stub_classrooms(*_args, **_kwargs):
        return [
            make_classroom(student_ids=[STUDENT_ID]),
            make_classroom(student_ids=[uuid4()]),
        ]

    current_user = make_user()

    async def get_by_id_stub(*_args, **_kwargs):
        return current_user

    monkeypatch.setattr(
        ClassroomService,
        "list_classrooms",
        list_stub_classrooms,
    )
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, current_user)

    response = client.get("/api/classrooms")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["name"] == "AI 기초"


def test_list_classrooms_requires_login(client):
    response = client.get("/api/classrooms")

    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTH__UNAUTHORIZED"


def test_create_classroom_returns_200_for_professor(client, monkeypatch):
    async def create_stub_classroom(*_args, **_kwargs):
        return make_classroom(professor_ids=[PROFESSOR_ID, OTHER_PROFESSOR_ID])

    professor_user = make_user(role=UserRole.PROFESSOR, user_id=PROFESSOR_ID)

    async def get_by_id_stub(*_args, **_kwargs):
        return professor_user

    monkeypatch.setattr(
        ClassroomService,
        "create_classroom",
        create_stub_classroom,
    )
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, professor_user)

    response = client.post(
        "/api/classrooms",
        json={
            "name": "AI 기초",
            "professor_ids": [str(OTHER_PROFESSOR_ID)],
            "grade": 3,
            "semester": "1학기",
            "section": "01",
            "description": "AI 입문 강의실",
            "student_ids": [str(STUDENT_ID)],
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["professor_ids"] == [
        str(PROFESSOR_ID),
        str(OTHER_PROFESSOR_ID),
    ]


def test_create_classroom_returns_403_for_student(client, monkeypatch):
    student_user = make_user(role=UserRole.STUDENT)

    async def get_by_id_stub(*_args, **_kwargs):
        return student_user

    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, student_user)

    response = client.post(
        "/api/classrooms",
        json={
            "name": "AI 기초",
            "professor_ids": [str(PROFESSOR_ID)],
            "grade": 3,
            "semester": "1학기",
            "section": "01",
            "student_ids": [str(STUDENT_ID)],
        },
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "AUTH__FORBIDDEN"


def test_get_classroom_returns_403_for_other_organization(client, monkeypatch):
    async def get_stub_classroom(*_args, **_kwargs):
        return make_classroom()

    other_org_user = make_user(organization_id=OTHER_ORG_ID)

    async def get_by_id_stub(*_args, **_kwargs):
        return other_org_user

    monkeypatch.setattr(ClassroomService, "get_classroom", get_stub_classroom)
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, other_org_user)

    response = client.get(f"/api/classrooms/{make_classroom().id}")

    assert response.status_code == 403
    assert response.json()["error_code"] == "AUTH__FORBIDDEN"


def test_update_classroom_returns_200_for_professor_member(
    client,
    monkeypatch,
):
    async def get_stub_classroom(*_args, **_kwargs):
        return make_classroom()

    async def update_stub_classroom(*_args, **_kwargs):
        classroom = make_classroom()
        classroom.name = "AI 심화"
        return classroom

    professor_user = make_user(role=UserRole.PROFESSOR, user_id=PROFESSOR_ID)

    async def get_by_id_stub(*_args, **_kwargs):
        return professor_user

    monkeypatch.setattr(ClassroomService, "get_classroom", get_stub_classroom)
    monkeypatch.setattr(
        ClassroomService,
        "update_classroom",
        update_stub_classroom,
    )
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, professor_user)

    response = client.patch(
        f"/api/classrooms/{make_classroom().id}",
        json={"name": "AI 심화"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "AI 심화"


def test_update_classroom_returns_403_for_non_member_professor(
    client,
    monkeypatch,
):
    async def get_stub_classroom(*_args, **_kwargs):
        return make_classroom()

    professor_user = make_user(
        role=UserRole.PROFESSOR,
        user_id=OTHER_PROFESSOR_ID,
    )

    async def get_by_id_stub(*_args, **_kwargs):
        return professor_user

    monkeypatch.setattr(ClassroomService, "get_classroom", get_stub_classroom)
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, professor_user)

    response = client.patch(
        f"/api/classrooms/{make_classroom().id}",
        json={"name": "AI 심화"},
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "AUTH__FORBIDDEN"


def test_delete_classroom_returns_200_for_admin(client, monkeypatch):
    async def get_stub_classroom(*_args, **_kwargs):
        return make_classroom()

    async def delete_stub_classroom(*_args, **_kwargs):
        return make_classroom()

    admin_user = make_user(role=UserRole.ADMIN, user_id=ADMIN_ID)

    async def get_by_id_stub(*_args, **_kwargs):
        return admin_user

    monkeypatch.setattr(ClassroomService, "get_classroom", get_stub_classroom)
    monkeypatch.setattr(
        ClassroomService,
        "delete_classroom",
        delete_stub_classroom,
    )
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, admin_user)

    response = client.delete(f"/api/classrooms/{make_classroom().id}")

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "AI 기초"


def test_create_classroom_duplicate_returns_409(client, monkeypatch):
    async def raise_duplicate_classroom(*_args, **_kwargs):
        raise ClassroomAlreadyExistsException()

    professor_user = make_user(role=UserRole.PROFESSOR, user_id=PROFESSOR_ID)

    async def get_by_id_stub(*_args, **_kwargs):
        return professor_user

    monkeypatch.setattr(
        ClassroomService,
        "create_classroom",
        raise_duplicate_classroom,
    )
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, professor_user)

    response = client.post(
        "/api/classrooms",
        json={
            "name": "AI 기초",
            "professor_ids": [str(PROFESSOR_ID)],
            "grade": 3,
            "semester": "1학기",
            "section": "01",
            "student_ids": [str(STUDENT_ID)],
        },
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "CLASSROOM__ALREADY_EXISTS"


def test_get_classroom_not_found_returns_404(client, monkeypatch):
    async def raise_not_found(*_args, **_kwargs):
        raise ClassroomNotFoundException()

    current_user = make_user()

    async def get_by_id_stub(*_args, **_kwargs):
        return current_user

    monkeypatch.setattr(ClassroomService, "get_classroom", raise_not_found)
    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, current_user)

    response = client.get(f"/api/classrooms/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "CLASSROOM__NOT_FOUND"


def test_create_classroom_invalid_input_returns_422(client, monkeypatch):
    professor_user = make_user(role=UserRole.PROFESSOR, user_id=PROFESSOR_ID)

    async def get_by_id_stub(*_args, **_kwargs):
        return professor_user

    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, professor_user)

    response = client.post(
        "/api/classrooms",
        json={
            "name": "A",
            "professor_ids": [],
            "grade": 0,
            "semester": "",
            "section": "",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "SERVER__REQUEST_VALIDATION_ERROR"


def test_update_classroom_empty_patch_returns_422(client, monkeypatch):
    professor_user = make_user(role=UserRole.PROFESSOR, user_id=PROFESSOR_ID)

    async def get_by_id_stub(*_args, **_kwargs):
        return professor_user

    monkeypatch.setattr(UserSQLAlchemyRepository, "get_by_id", get_by_id_stub)
    set_access_token_cookie(client, professor_user)

    response = client.patch(f"/api/classrooms/{make_classroom().id}", json={})

    assert response.status_code == 422
    assert response.json()["error_code"] == "SERVER__REQUEST_VALIDATION_ERROR"
