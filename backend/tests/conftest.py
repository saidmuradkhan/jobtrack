import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    return User.objects.create_user(username="said", password="s3cure-pass-123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="rival", password="s3cure-pass-123")


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    api = APIClient()
    api.force_authenticate(user)
    return api
