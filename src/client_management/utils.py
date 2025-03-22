from typing import Type

from django.db.models import TextChoices


def get_choice_from_label(choices_class: Type[TextChoices], label: str):
    for choice in choices_class:
        if choice.label == label:
            return choice
    raise ValueError(f"Invalid label '{label}' for choices class '{choices_class.__name__}'")
