import re

import pytest
from django.test import RequestFactory

from client_management.controllers.client_invite import ClientInviter


@pytest.fixture
def sample_invite_email_template():
    return """Hi Test,

Welcome to Chloe Leanne Fitness!

Please use the link below to set your password.

[Reset
Password](http://testserver/accounts/reset/USER_ID/RANDOM_KEY/)

Please don't hesitate to get in touch if you have any questions or need
clarifications.

Best regards,

Chloe

"""


def test_send_client_invite(business_client, mailoutbox, sample_invite_email_template):
    assert len(mailoutbox) == 0

    client_inviter = ClientInviter(business_client.pk, RequestFactory().get('/'))

    assert client_inviter.context['first_name'] == 'Test'
    assert client_inviter.context['last_name'] == 'User'
    assert re.match(
        r'^http://testserver/accounts/reset/[A-Za-z0-9_\-]+/[A-Za-z0-9\-]+/$',
        client_inviter.context['password_reset_link']
    )

    client_inviter.send_client_invite()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].content_subtype == 'html' or 'plain'
    assert mailoutbox[0].subject == 'Invitation to Test User'
    assert mailoutbox[0].to == [business_client.user.email]
    assert re.sub(
        r'http://testserver/accounts/reset/[^/]+/[^/]+/',
        'http://testserver/accounts/reset/USER_ID/RANDOM_KEY/',
        mailoutbox[0].body
    ) == sample_invite_email_template
