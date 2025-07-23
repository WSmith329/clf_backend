import logging

import html2text
import sentry_sdk
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from client_management.models import Client

logger = logging.getLogger(__name__)


class ClientInviter:
    INVITE_EMAIL_TEMPLATE = 'client_management/client_invite_email.html'

    def __init__(self, client_pk, request):
        self.client = Client.objects.get(pk=client_pk)
        self.request = request
        self.context = self._build_template_context()

    def _build_template_context(self):
        return {
            'first_name': self.client.user.first_name,
            'last_name': self.client.user.last_name,
            'password_reset_link': self.generate_reset_password_link()
        }

    def generate_reset_password_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.client.user.pk))
        token = default_token_generator.make_token(self.client.user)

        return self.request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

    def send_client_invite(self):
        try:
            subject = f'Invitation to {self.client.user.get_full_name()}'
            body = render_to_string(self.INVITE_EMAIL_TEMPLATE, self.context)

            self.client.user.email_user(subject, html2text.html2text(body), settings.EMAIL_HOST_USER, html_message=body)
        except Exception as e:
            logger.exception(f'Invite processing for {self.client} failed: {e}')
            sentry_sdk.capture_exception(e)
            raise e

