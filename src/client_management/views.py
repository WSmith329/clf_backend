import datetime

from constance import config
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods

from .forms import MeasurementRecordingForm, PaymentRequestForm, SubscriptionFormSet, StartingInvoiceNumberForm
from .models import Payment, Subscription


@require_http_methods(['GET', 'POST'])
def measurement_recording(request):
    if request.method == 'POST':
        form = MeasurementRecordingForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('account')

    else:
        form = MeasurementRecordingForm()

    return render(request, 'client_management/measurement_recording.html',
                  {'title': 'Enter new recording', 'form': form})


def payments_index(request, payment_status):
    if not Payment.objects.exists() and not request.session.get('skip_set_starting_invoice_number', False):
        return redirect('set_starting_invoice_number')

    payment_status = Payment.get_payment_status_from_label(payment_status.title())
    payments = Payment.objects.filter(status=payment_status).order_by('due_date')

    paginator = Paginator(payments, 20)
    page = paginator.get_page(request.GET.get('page'))

    actions = {
        Payment.PaymentStatuses.DRAFT.value: [
            ('Edit', reverse('update_payment_request', args=[0])[:-2], 'neutral'),
            ('Request', reverse('send_payment_request', args=[0])[:-2], 'green'),  # 0 acts as a placeholder
            ('Void', reverse('mark_payment_as_void', args=[0])[:-2], 'red')
        ],
        Payment.PaymentStatuses.REQUESTED.value: [
            ('Complete', reverse('mark_payment_as_completed', args=[0])[:-2], 'green'),
            ('Void', reverse('mark_payment_as_void', args=[0])[:-2], 'red')
        ],
        Payment.PaymentStatuses.COMPLETED.value: [],
        Payment.PaymentStatuses.VOID.value: []
    }

    group_actions = {
        Payment.PaymentStatuses.DRAFT.value: [
            ('send_requests', 'Send Requests'),
            ('void_payments', 'Mark as Void')
        ],
        Payment.PaymentStatuses.REQUESTED.value: [
            ('complete_payments', 'Mark as Completed'),
            ('void_payments', 'Mark as Void')
        ],
        Payment.PaymentStatuses.COMPLETED.value: [],
        Payment.PaymentStatuses.VOID.value: []
    }

    return render(request, 'client_management/payments_index.html', {
        'title': 'Client payments',
        'payment_statuses': [status for status in Payment.PaymentStatuses],
        'chosen_status': payment_status,
        'payments': payments,
        'actions': actions[payment_status],
        'group_actions': group_actions[payment_status],
        'page': page
    })


def create_payment_request(request, pk=None):
    if pk:
        payment = get_object_or_404(Payment, pk=pk)
    else:
        payment = None

    if request.method == 'POST':
        payment_form = PaymentRequestForm(request.POST, instance=payment)
        subscription_formset = SubscriptionFormSet(request.POST, instance=payment)

        if payment_form.is_valid() and subscription_formset.is_valid():
            payment = payment_form.save()
            subscriptions = subscription_formset.save(commit=False)
            for subscription in subscriptions:
                subscription.payment = payment
                subscription.save()
            subscription_formset.save_m2m()
            return redirect('payments_index', Payment.draft_status_in_url_format())

    else:
        payment_form = PaymentRequestForm(instance=payment)
        subscription_formset = SubscriptionFormSet(instance=payment)

    return render(request, 'client_management/create_payment_request.html', {
        'title': 'Create a new payment request' if not payment else 'Update payment request',
        'invoice_code': payment.invoice_code if payment else Payment.generate_invoice_code(),
        'payment_form': payment_form,
        'subscription_formset': subscription_formset,
    })


def set_starting_invoice_number(request):
    if request.method == 'POST':
        form = StartingInvoiceNumberForm(request.POST)
        if form.is_valid():
            if starting_invoice_number := form.cleaned_data['starting_invoice_number']:
                config.STARTING_INVOICE_NUMBER = starting_invoice_number
            request.session['skip_set_starting_invoice_number'] = True
            messages.success(request, 'Starting invoice number set.'
                                      f'The first invoice code will be {Payment.generate_invoice_code()}.')
            return redirect(
                'payments_index',
                Payment.draft_status_in_url_format()
            )

    else:
        default_number = Payment.generate_invoice_code()
        form = StartingInvoiceNumberForm()
        return render(request, 'client_management/set_starting_invoice_number.html', context={
            'title': 'Starting invoice number',
            'default_number': Payment.generate_invoice_code(),
            'form': form,
            'message': mark_safe(
                '<p>Before handling payments and invoices, let\'s set the number you want to start your invoice codes'
                f' from!</p><p>By default, this will be <b>{config.STARTING_INVOICE_NUMBER}</b> so the first invoice'
                f' code will be <b>{default_number}</b>.</p>'
            )
        })


def send_payment_request(request, pk):
    payment = Payment.objects.get(pk=pk)
    payment.request()

    messages.success(request, f'Sent request for {payment.invoice_code} to {payment.client.user.email}.')
    return redirect('payments_index', Payment.requested_status_in_url_format())


def mark_payment_as_completed(request, pk):
    payment = Payment.objects.get(pk=pk)
    payment.set_as_completed()

    messages.success(request, f'Marked {payment.invoice_code} as completed.')
    return redirect('payments_index', Payment.completed_status_in_url_format())


def mark_payment_as_void(request, pk):
    payment = Payment.objects.get(pk=pk)
    payment.set_as_void()

    messages.success(request, f'Marked {payment.invoice_code} as void.')
    return redirect('payments_index', Payment.void_status_in_url_format())


def process_selected_payments(request):
    if request.method == 'POST':
        selected_payments = request.POST.getlist('selected_payments')
        action = request.POST.get('action')

        if not selected_payments:
            messages.error(request, 'No payments selected.')
            return redirect('payments_index', Payment.draft_status_in_url_format())

        match action:
            case 'send_requests':
                for pk in selected_payments:
                    payment = Payment.objects.get(pk=pk)
                    payment.request()
                messages.success(request, f'Sent requests for {len(selected_payments)} payments.')
                return redirect('payments_index', Payment.requested_status_in_url_format())

            case 'complete_payments':
                Payment.objects.filter(pk__in=selected_payments).update(status=Payment.PaymentStatuses.COMPLETED.value)
                messages.success(request, f'Marked {len(selected_payments)} payments as completed.')
                return redirect('payments_index', Payment.completed_status_in_url_format())

            case 'void_payments':
                Payment.objects.filter(pk__in=selected_payments).update(status=Payment.PaymentStatuses.VOID.value)
                messages.success(request, f'Marked {len(selected_payments)} payments as void.')
                return redirect('payments_index', Payment.void_status_in_url_format())

    return redirect('payments_index', Payment.draft_status_in_url_format())
