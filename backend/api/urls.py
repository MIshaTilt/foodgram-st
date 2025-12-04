from django.urls import path, include
from rest_framework.routers import DefaultRouter

# УБРАЛИ TokenCreateView и TokenLogoutView из импорта
from api.views import (
    UserViewSet, IngredientViewSet, RecipeViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
