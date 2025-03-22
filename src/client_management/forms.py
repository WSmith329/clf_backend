from django.forms import ModelForm, DateField, forms, widgets, BooleanField, inlineformset_factory, IntegerField, \
    DateInput
from django.utils import timezone

from client_management.models import MeasurementRecording, Payment, Subscription


class MeasurementRecordingForm(ModelForm):
    class Meta:
        model = MeasurementRecording
        fields = ['weight', 'height', 'body_fat', 'bmi']

    def save(self, commit=True, user=None):
        measurement_recording = super(MeasurementRecordingForm, self).save(commit=False)

        measurement_recording.recorded = timezone.now()

        if user and hasattr(user, 'client'):
            measurement_recording.client = user.client

        if commit:
            measurement_recording.save()
        return measurement_recording


class CompletedDateForm(forms.Form):
    completed_date = DateField(
        required=False,
        widget=widgets.DateInput(attrs={'type': 'date'}),
        help_text='Leave blank to automatically set to today.'
    )
    ignore_unpaid = BooleanField(
        required=False,
        help_text='This only applies if the amount paid does not match the amount due.'
    )


class PaymentRequestForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice_code', 'client', 'amount_due', 'due_date', 'notes']


SubscriptionFormSet = inlineformset_factory(
    Payment,
    Subscription,
    fields=('service', 'weeks', 'sessions'),
    extra=1,
    can_delete=True
)


class StartingInvoiceNumberForm(forms.Form):
    starting_invoice_number = IntegerField(required=False, min_value=0, help_text='Leave blank to accept default.')
