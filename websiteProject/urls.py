from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('set-language/', set_language, name='set_language'),
    ]

urlpatterns += i18n_patterns(
path('', include('mainapp.urls', namespace='mainapp')),
    path('users/', include('users.urls', namespace='users')),
    path('galleryapp/', include('gallery.urls', namespace='gallery')),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)