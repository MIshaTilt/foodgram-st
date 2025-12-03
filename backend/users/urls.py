from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, TokenCreateView, TokenLogoutView

router = DefaultRouter()
# The router for custom user list/retrieve/subscribe actions
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),

    path('auth/', include('djoser.urls.jwt')),

    path('', include(router.urls)),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenLogoutView.as_view(), name='logout')

]
