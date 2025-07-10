from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def mark_notifications_seen(request):
    Notification.objects.filter(user=request.user, seen=False).update(seen=True)
    return JsonResponse({'success': True})
