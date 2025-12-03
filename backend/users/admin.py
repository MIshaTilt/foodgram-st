from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import User
from .models import Subscription

# ...и регистрируем её в админке:
admin.site.register(Subscription)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Отображаемые поля в списке
    list_display = (
        'id', 
        'username', 
        'email', 
        'first_name', 
        'last_name', 
    )
    
    # ТРЕБОВАНИЕ: Поиск по имени и email
    search_fields = ('username', 'email') 
    
    # Фильтры справа (опционально, но удобно)
    list_filter = ('username', 'email')
