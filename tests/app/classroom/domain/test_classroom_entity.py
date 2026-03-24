from uuid import UUID

from app.classroom.domain.entity import Classroom

ORG_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("22222222-2222-2222-2222-222222222222")


def test_classroom_delete_sets_inactive():
    classroom = Classroom(
        organization_id=ORG_ID,
        instructor_id=USER_ID,
        code="ai-101",
        name="AI 기초",
        term="2026-1",
    )

    classroom.delete()

    assert classroom.is_active is False
