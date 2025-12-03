from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # API endpoints prefixed with '/api/'
    # This includes the users endpoints (djoser auth, user list, subscribe)
    path('api/', include('users.urls')),

    # This includes the recipes endpoints (ingredients, recipes, shopping cart)
    path('api/', include('recipes.urls')),
]
