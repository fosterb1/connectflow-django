from django.urls import path, include
from rest_framework import routers
from apps.accounts.api_views import UserViewSet
from apps.organizations.api_views import OrganizationViewSet, DepartmentViewSet, TeamViewSet, SharedProjectViewSet
from apps.chat_channels.api_views import ChannelViewSet, MessageViewSet
from apps.support.api_views import TicketViewSet, TicketMessageViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'projects', SharedProjectViewSet, basename='project')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'ticket-messages', TicketMessageViewSet, basename='ticket-message')

urlpatterns = [
    path('', include(router.urls)),
]
