from django.contrib import admin

# Register your models here.
from .models import User
from .models import Subscription

# ...и регистрируем её в админке:
admin.site.register(User)
admin.site.register(Subscription)