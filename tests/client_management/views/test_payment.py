import datetime

import pytest
from constance import config
from django.urls import reverse

from client_management.models import Payment
from config.factories.client_management import ServiceFactory, PaymentFactory


@pytest.mark.parametrize('status, django_client, expected_response_status', [
        pytest.param(Payment.PaymentStatuses.DRAFT.label, 'staff_user_client', 200,
                     id='draft-by-staff'),
        pytest.param(Payment.PaymentStatuses.REQUESTED.label, 'staff_user_client', 200,
                     id='requested-by-staff'),
        pytest.param(Payment.PaymentStatuses.COMPLETED.label, 'staff_user_client', 200,
                     id='completed-by-staff'),
        pytest.param(Payment.PaymentStatuses.VOID.label, 'staff_user_client', 200,
                     id='void-by-staff'),
        pytest.param(Payment.PaymentStatuses.DRAFT.label, 'client_user_client', 302,
                     id='draft-by-client'),
        pytest.param(Payment.PaymentStatuses.REQUESTED.label, 'client_user_client', 302,
                     id='requested-by-client'),
        pytest.param(Payment.PaymentStatuses.COMPLETED.label, 'client_user_client', 302,
                     id='completed-by-client'),
        pytest.param(Payment.PaymentStatuses.VOID.label, 'client_user_client', 302,
                     id='void-by-client')
    ]
)
def test_payments_index_get(status, django_client, expected_response_status, payment, request):
    django_client = request.getfixturevalue(django_client)

    response = django_client.get(
        reverse('payments_index', args=[status])
    )
    assert response.status_code == expected_response_status


@pytest.mark.parametrize('status', [
        pytest.param(Payment.PaymentStatuses.DRAFT.label),
        pytest.param(Payment.PaymentStatuses.REQUESTED.label),
        pytest.param(Payment.PaymentStatuses.COMPLETED.label),
        pytest.param(Payment.PaymentStatuses.VOID.label)
    ]
)
def test_payments_index_get_with_no_payment(staff_user_client, status):
    response = staff_user_client.get(
        reverse('payments_index', args=[status])
    )
    assert response.status_code == 302
    assert response.url == reverse('set_starting_invoice_number')


def test_create_payment_request_get(staff_user_client):
    response = staff_user_client.get(
        reverse('create_payment_request')
    )
    assert response.status_code == 200
    assert not Payment.objects.count()


def test_create_payment_request_post(staff_user_client, client_user, service):
    assert not Payment.objects.count()

    invoice_code = 'INV00008'
    amount_due = 120
    due_date = datetime.date(2025, 3, 28)

    subscription_weeks = 4
    subscription_sessions = 1

    response = staff_user_client.post(
        reverse('create_payment_request'),
        data={
            'invoice_code': [invoice_code],
            'client': [client_user.client.pk],
            'amount_due': [amount_due],
            'due_date': [due_date],
            'notes': [''],
            'subscription_set-TOTAL_FORMS': ['1'],
            'subscription_set-INITIAL_FORMS': ['0'],
            'subscription_set-MIN_NUM_FORMS': ['0'],
            'subscription_set-MAX_NUM_FORMS': ['1000'],
            'subscription_set-0-service': [service.pk],
            'subscription_set-0-weeks': [subscription_weeks],
            'subscription_set-0-sessions': [subscription_sessions]
        }
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[Payment.draft_status_in_url_format()])

    assert Payment.objects.count() == 1
    assert (payment := Payment.objects.get(invoice_code=invoice_code))
    assert payment.client == client_user.client
    assert payment.amount_due == amount_due
    assert payment.due_date == due_date
    assert not payment.notes

    assert payment.subscription_set.count() == 1
    subscription = payment.subscription_set.first()
    assert subscription.service == service
    assert subscription.weeks == subscription_weeks
    assert subscription.sessions == subscription_sessions


def test_update_payment_request_get(staff_user_client, payment):
    response = staff_user_client.get(
        reverse('update_payment_request', args=[payment.pk])
    )
    assert response.status_code == 200
    assert Payment.objects.count() == 1


def test_update_payment_request_post(staff_user_client, client_user, payment, service):
    assert Payment.objects.count() == 1

    subscription_weeks = 4
    subscription_sessions = 1

    subscription = payment.subscription_set.create(
        service=service,
        weeks=subscription_weeks,
        sessions=subscription_sessions
    )

    updated_due_date = datetime.date(2025, 2, 28)
    second_service = ServiceFactory()

    assert not payment.subscription_set.filter(pk=second_service.pk)
    assert not Payment.objects.filter(due_date=updated_due_date)

    response = staff_user_client.post(
        reverse('update_payment_request', args=[payment.pk]),
        data={
            'invoice_code': [payment.invoice_code],
            'client': [payment.client.pk],
            'amount_due': [payment.amount_due],
            'due_date': [updated_due_date],
            'notes': [payment.notes],
            'subscription_set-TOTAL_FORMS': ['2'],
            'subscription_set-INITIAL_FORMS': ['1'],
            'subscription_set-MIN_NUM_FORMS': ['0'],
            'subscription_set-MAX_NUM_FORMS': ['1000'],
            'subscription_set-0-service': [service.pk],
            'subscription_set-0-weeks': [subscription_weeks],
            'subscription_set-0-sessions': [subscription_sessions],
            'subscription_set-0-id': [subscription.pk],
            'subscription_set-0-payment': [payment.pk],
            'subscription_set-1-service': [second_service.pk],
            'subscription_set-1-weeks': [subscription_weeks],
            'subscription_set-1-sessions': [subscription_sessions],
            'subscription_set-1-id': [''],
            'subscription_set-1-payment': [payment.pk],
        }
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[Payment.draft_status_in_url_format()])

    payment.refresh_from_db()
    assert payment.due_date == updated_due_date
    assert payment.subscription_set.count() == 2


def test_set_starting_invoice_number_get(staff_user_client, payment):
    response = staff_user_client.get(
        reverse('set_starting_invoice_number')
    )
    assert response.status_code == 200


def test_set_starting_invoice_number_post(staff_user_client):
    assert config.STARTING_INVOICE_NUMBER == 1
    response = staff_user_client.post(
        reverse('set_starting_invoice_number'),
        data={
            'starting_invoice_number': [100]
        }
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[Payment.draft_status_in_url_format()])

    assert config.STARTING_INVOICE_NUMBER == 100


def test_send_payment_request(staff_user_client, payment, mailoutbox):
    assert payment.status == Payment.PaymentStatuses.DRAFT.value
    assert len(mailoutbox) == 0

    response = staff_user_client.get(
        reverse('send_payment_request', args=[payment.pk])
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[Payment.requested_status_in_url_format()])

    payment.refresh_from_db()
    assert payment.status == Payment.PaymentStatuses.REQUESTED.value
    assert len(mailoutbox) == 1


def test_mark_payment_as_completed(staff_user_client, requested_payment):
    assert requested_payment.status == Payment.PaymentStatuses.REQUESTED.value

    response = staff_user_client.get(
        reverse('mark_payment_as_completed', args=[requested_payment.pk])
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[Payment.completed_status_in_url_format()])

    requested_payment.refresh_from_db()
    assert requested_payment.status == Payment.PaymentStatuses.COMPLETED.value
    assert requested_payment.completed_date == datetime.date.today()


@pytest.mark.parametrize('starting_payment, starting_status', [
    pytest.param('payment', Payment.PaymentStatuses.DRAFT.value, id='from-draft'),
    pytest.param('requested_payment', Payment.PaymentStatuses.REQUESTED.value, id='from-requested')
])
def test_mark_payment_as_void(staff_user_client, starting_payment, starting_status, request):
    payment = request.getfixturevalue(starting_payment)
    assert payment.status == starting_status

    response = staff_user_client.get(
        reverse('mark_payment_as_void', args=[payment.pk])
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[Payment.void_status_in_url_format()])

    payment.refresh_from_db()
    assert payment.status == Payment.PaymentStatuses.VOID.value


def test_process_selected_payments_send_requests(staff_user_client, business_client, mailoutbox):
    payments = PaymentFactory.create_batch(3, client=business_client)

    assert len(mailoutbox) == 0
    for payment in payments:
        assert payment.status == Payment.PaymentStatuses.DRAFT.value

    response = staff_user_client.post(
        reverse('process_selected_payments'),
        data={
            'selected_payments': [payment.pk for payment in payments],
            'action': 'send_requests'
        }
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[Payment.requested_status_in_url_format()])

    assert len(mailoutbox) == 3
    for payment in payments:
        payment.refresh_from_db()
        assert payment.status == Payment.PaymentStatuses.REQUESTED.value


@pytest.mark.parametrize('starting_status, action, expected_end_status', [
    pytest.param(
        Payment.PaymentStatuses.DRAFT.value,
        'void_payments',
        Payment.PaymentStatuses.VOID,
        id='mark-draft-as-void'
    ),
    pytest.param(
        Payment.PaymentStatuses.REQUESTED.value,
        'complete_payments',
        Payment.PaymentStatuses.COMPLETED,
        id='mark-requested-as-completed'
    ),
    pytest.param(
        Payment.PaymentStatuses.REQUESTED.value,
        'void_payments',
        Payment.PaymentStatuses.VOID,
        id='mark-requested-as-void'
    )
])
def test_process_selected_payments_mark_as_status(starting_status, expected_end_status, action,
                                                  staff_user_client, business_client):
    payments = PaymentFactory.create_batch(3, client=business_client, status=starting_status)

    for payment in payments:
        assert payment.status == starting_status

    response = staff_user_client.post(
        reverse('process_selected_payments'),
        data={
            'selected_payments': [payment.pk for payment in payments],
            'action': action
        }
    )
    assert response.status_code == 302
    assert response.url == reverse('payments_index', args=[expected_end_status.label.lower()])

    for payment in payments:
        payment.refresh_from_db()
        assert payment.status == expected_end_status.value
