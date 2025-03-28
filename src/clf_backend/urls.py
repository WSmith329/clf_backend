"""
URL configuration for clf_backend project.
"""
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin.sites import site
from django.urls import include, path

from clf_backend import views

site.site_title = 'Chloe Leanne Fitness'
site.site_header = 'Chloe Leanne Fitness'
site.enable_nav_sidebar = True

urlpatterns = (([
    path('admin/', admin.site.urls),
    path('', login_required(views.dashboard), name='dashboard'),
    path('accounts/', login_required(views.account), name='account'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('client_management.urls')),
]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
