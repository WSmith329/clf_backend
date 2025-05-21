import secrets
import string
from typing import Type

from django.db.models import TextChoices


def get_choice_from_label(choices_class: Type[TextChoices], label: str):
    for choice in choices_class:
        if choice.label == label:
            return choice
    raise ValueError(f"Invalid label '{label}' for choices class '{choices_class.__name__}'")


def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))