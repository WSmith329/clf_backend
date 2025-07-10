from feed.models import Notification


def notifications_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).select_related('action')
        has_new_notification = notifications.filter(seen=False).exists()
        unread_count = notifications.filter(seen=False).count()
    else:
        notifications = []
        has_new_notification = False
        unread_count = 0
    return {
        'notifications': notifications,
        'has_new_notification': has_new_notification,
        "unread_count": unread_count
    }
