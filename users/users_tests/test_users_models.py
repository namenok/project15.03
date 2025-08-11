import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_profile_creation():
    user = User.objects.create_user(username="testuser", password="pass1234")
    profile = user.profile
    profile.bio = "Test bio"
    profile.save()

    assert profile.user == user
    assert profile.bio == "Test bio"
    assert str(profile) == user.username



@pytest.mark.django_db
def test_profile_save():
    user = User.objects.create_user(username="saveuser", password="pass1234")
    profile = user.profile
    profile.bio = "Updated bio"
    profile.save()

    profile.refresh_from_db()
    assert profile.bio == "Updated bio"
