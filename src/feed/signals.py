from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from feed.models import Action, Visibility, Subscription, Notification

User = get_user_model()


@receiver(post_save, sender=Action)
def notify_subscribers(sender, instance: Action, created, **kwargs):
    if not created or instance.visibility != Visibility.PUBLIC.value:
        return
    for subscription in Subscription.objects.for_actor(instance.actor):
        Notification.objects.get_or_create(user=subscription.user, action=instance)


@receiver(post_save, sender=User)
def create_subscriptions_on_user_creation(sender, instance: User, created, **kwargs):
    if created:
        Subscription.get_or_create(
            user=instance,
            actor=instance
        )

        for user in User.objects.filter(is_staff=True):
            Subscription.get_or_create(
                user=user,
                actor=instance
            )
