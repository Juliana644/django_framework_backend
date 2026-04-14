from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from tickets.views import TicketViewSet
from accounts.views import RegisterView, ProfileView

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth JWT
    path('api/auth/login/',    TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/refresh/',  TokenRefreshView.as_view(),   name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(),       name='register'),
    path('api/auth/profil/',   ProfileView.as_view(),        name='profil'),
    # Tickets
    path('api/', include(router.urls)),
]