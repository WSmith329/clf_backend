from django.contrib.auth.models import User
from django.urls import reverse

from client_management.models import Client


def test_create_client_post_success(staff_user_client, mailoutbox):
    assert len(mailoutbox) == 0
    assert not User.objects.filter(
        email='test@user.com',
        username='test@user.com',
        first_name='Test',
        last_name='User'
    )

    response = staff_user_client.post(
        reverse('create_client'),
        data={'email': 'test@user.com', 'first_name': 'Test', 'last_name': 'User'},
        follow=True
    )
    assert response.status_code == 200
    assert response.redirect_chain[0] == (reverse('manage_clients'), 302)

    assert (created_user := User.objects.get(
        email='test@user.com',
        username='test@user.com',
        first_name='Test',
        last_name='User'
    ))
    assert Client.objects.get(user=created_user)

    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == 'Invitation to Test User'
    assert mailoutbox[0].to == [created_user.email]


def test_create_client_post_existing_email(django_user_model, staff_user_client, mailoutbox):
    email = 'test@user.com'
    django_user_model.objects.create_user(email=email, username=email)

    assert len(mailoutbox) == 0

    response = staff_user_client.post(
        reverse('create_client'),
        data={'email': email, 'first_name': 'Test', 'last_name': 'User'},
        follow=True
    )
    assert response.status_code == 200
    assert not response.redirect_chain
    assert response.context_data['form'].errors['email'][0] == 'A user with that email already exists.'
