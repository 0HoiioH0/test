import pytest
from app.user.domain.entity.user import User

def test_user_entity_creation():
    # Given
    email = "test@example.com"
    nickname = "tester"
    
    # When
    user = User(email=email, nickname=nickname)
    
    # Then
    assert user.email == email
    assert user.nickname == nickname
    assert user.id is not None
    assert user.is_active is True

def test_user_update_nickname():
    # Given
    user = User(email="test@example.com", nickname="old")
    
    # When
    user.update_nickname("new")
    
    # Then
    assert user.nickname == "new"
