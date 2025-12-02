from django.contrib import admin

# Register your models here.
from .models import Recipe
from .models import Ingredient
from .models import IngredientInRecipe
from .models import Favorite
from .models import ShoppingCart

# ...и регистрируем её в админке:
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)