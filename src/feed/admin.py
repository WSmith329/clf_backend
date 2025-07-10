from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from feed.models import Subscription, Notification, Action


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('actor', 'verb', 'timestamp')
    search_fields = ('actor', 'verb')
    list_filter = (
        ('timestamp', DateRangeFilter),
        'actor_content_type',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'actor_content_type', 'created')
    search_fields = ('user', )
    list_filter = (
        ('created', DateRangeFilter),
        'actor_content_type',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'seen', 'created')
    search_fields = ('user', )
    list_filter = (
        ('created', DateRangeFilter),
        'seen',
    )