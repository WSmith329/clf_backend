import pytest
from django.test import Client as Django_Client

from client_management.models import Client


@pytest.fixture
def admin_user(db, django_user_model):
    return django_user_model.objects.create_superuser(
        username='admin',
        password='admin_pass',
    )


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username='test_user',
        password='test_pass',
        email='user@testmail.com',
        first_name='Test'
    )


@pytest.fixture
def business_client(user):
    return Client.objects.create(
        user=user
    )


@pytest.fixture
def client_user(business_client):
    return business_client.user


@pytest.fixture
def user_password():
    return 'test_pass'


@pytest.fixture()
def admin_user_client(admin_user):
    client = Django_Client()
    client.force_login(admin_user)
    return client


@pytest.fixture()
def client_user_client(client_user):
    client = Django_Client()
    client.force_login(client_user)
    return client
