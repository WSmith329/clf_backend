import datetime

from factory import django, fuzzy

from client_management.models import Payment, Service


class PaymentFactory(django.DjangoModelFactory):
    class Meta:
        model = Payment

    due_date = fuzzy.FuzzyDate(datetime.date.today())


class ServiceFactory(django.DjangoModelFactory):
    class Meta:
        model = Service
