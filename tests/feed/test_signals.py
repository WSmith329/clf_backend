import datetime

import freezegun
import pytest

from feed.controllers.log import log_public_action, log_private_action
from feed.models import Subscription, Notification


@freezegun.freeze_time(datetime.datetime(2025, 7, 8, 12, 15, 00))
def test_create_subscriptions_on_user_creation(django_user_model, staff_user):
    user = django_user_model.objects.create_user(
        username='test_user',
        password='test_pass',
        email='user@testmail.com',
        first_name='Test',
        last_name='User'
    )
    assert Subscription.objects.for_actor(user).get(
        user=user,
        created=datetime.datetime.now()
    )
    assert Subscription.objects.for_actor(user).get(
        user=staff_user,
        created=datetime.datetime.now()
    )


@pytest.mark.parametrize('log_function, is_notified', [
    pytest.param(log_public_action, True, id='public'),
    pytest.param(log_private_action, False, id='private')
])
def test_notify_subscribers(log_function, is_notified, staff_user, client_user):
    Subscription.get_or_create(staff_user, client_user)
    action = log_function(client_user, 'logged in')
    assert Notification.objects.filter(user=client_user, action=action).exists() == is_notified
