from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, TokenCreateView, TokenLogoutView

router = DefaultRouter()
# The router for custom user list/retrieve/subscribe actions
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    # Include the standard Djoser URLs. This will map /token/login and /token/logout.
    # We will override the view handling for these paths in settings.py to use JWT.
    path('auth/', include('djoser.urls')),
    
    # Include Djoser's JWT URLs for refresh and verify only (since 'token' covers login)
    path('auth/', include('djoser.urls.jwt')),
    
    # Includes the router for custom user views (e.g., user list, subscription)
    path('', include(router.urls)),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenLogoutView.as_view(), name='logout')

]