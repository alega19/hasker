"""hasker URL Configuration"""

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import hashers


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include('api.urls', namespace='api')),
    url(r'^', include('hasker.urls'))
]


from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
