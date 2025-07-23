import logging

import sentry_sdk
from django.contrib.contenttypes.models import ContentType

from feed.models import Visibility, Action

logger = logging.getLogger(__name__)


def log_action(actor, verb, visibility, target=None, action_object=None, description='', **extra):
    logger.debug(f"Logging action: {actor} {verb} {action_object} {target}")

    try:
        if actor.pk is None:
            raise ValueError("Actor must be a saved model instance")
        if target and target.pk is None:
            raise ValueError("Target must be a saved model instance")
        if action_object and action_object.pk is None:
            raise ValueError("Action object must be a saved model instance")

        return Action.objects.create(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            verb=verb,
            target_content_type=ContentType.objects.get_for_model(target) if target else None,
            target_object_id=target.pk if target else None,
            action_object_content_type=ContentType.objects.get_for_model(action_object) if action_object else None,
            action_object_object_id=action_object.pk if action_object else None,
            description=description,
            visibility=visibility,
            extra=extra
        )
    except Exception as e:
        logger.exception(f'Action logging failed: {e}')
        sentry_sdk.capture_exception(e)
        raise e


def log_private_action(actor, verb, target=None, action_object=None, description=''):
    return log_action(actor, verb, Visibility.PRIVATE.value, target, action_object, description)


def log_public_action(actor, verb, target=None, action_object=None, description=''):
    return log_action(actor, verb, Visibility.PUBLIC.value, target, action_object, description)
