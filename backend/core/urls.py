from rest_framework.routers import SimpleRouter
from django.conf.urls import include
from django.urls import path
from core.views import StateViewSet, SubscriberViewSet, SubscriberPingViewSet

router = SimpleRouter()

router.register(r"states", StateViewSet, basename="state")
router.register(r"subscribers", SubscriberViewSet, basename="subscriber")
router.register(r"subscriber-pings", SubscriberPingViewSet, basename="subscriber-ping")

urlpatterns = [path("", include(router.urls))]