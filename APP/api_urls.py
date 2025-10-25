from django.urls import include, path
from rest_framework import routers
from django.conf.urls.static import static
from django.conf import settings

from account.api import UserViewSet
from scanned_text.api import ScannedTextViewSet

router = routers.DefaultRouter()
router.register(r'account', UserViewSet, basename="account")
router.register(r'scanned-texts', ScannedTextViewSet, basename="scanned-texts")



urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)