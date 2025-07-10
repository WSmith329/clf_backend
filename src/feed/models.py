from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SubscriptionManager(models.Manager):
    def for_actor(self, actor):
        return self.get_queryset().filter(
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk
        )


class Visibility(models.TextChoices):
    PRIVATE = 'PR', _('Private')
    PUBLIC = 'PU', _('Public')


class Action(models.Model):
    actor_content_type = models.ForeignKey(ContentType, related_name='actor_type', on_delete=models.CASCADE)
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType, related_name='target_type', on_delete=models.CASCADE, blank=True, null=True
    )
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType, related_name='action_object_type', on_delete=models.CASCADE, blank=True, null=True
    )
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    timestamp = models.DateTimeField(default=timezone.now)

    visibility = models.CharField(choices=Visibility, default=Visibility.PRIVATE, max_length=2)

    extra = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        context = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }

        if self.target and self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago') % context
        elif self.target:
            return _('%(actor)s %(verb)s %(target)s %(timesince)s ago') % context
        elif self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(timesince)s ago') % context
        else:
            return _('%(actor)s %(verb)s %(timesince)s ago') % context

    def timesince(self, now=None):
        from django.utils.timesince import timesince
        return timesince(self.timestamp, now)


class Subscription(models.Model):
    objects = SubscriptionManager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    actor_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    actor_object_id = models.PositiveIntegerField(blank=True, null=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    verb_filter = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'actor_content_type', 'actor_object_id')

    @classmethod
    def get_or_create(cls, user, actor, verb_filter=None):
        return cls.objects.get_or_create(
            user=user,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            verb_filter=verb_filter
        )


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
