from django.contrib import admin
from .models import Recipe, Ingredient, Favorite, ShoppingCart, IngredientInRecipe

# Для удобства можно выводить ингредиенты прямо внутри рецепта
class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites')
    readonly_fields = ('added_in_favorites',)
    
    # ТРЕБОВАНИЕ: Поиск по названию и автору
    # author__username означает "искать по полю username у связанного автора"
    search_fields = ('name', 'author__username')
    
    list_filter = ('author',)
    inlines = (IngredientInline,)

    # ТРЕБОВАНИЕ: Отображение общего числа добавлений в избранное
    @admin.display(description='В избранном')
    def added_in_favorites(self, obj):
        # obj.favorites — это related_name в модели Favorite. 
        # Если у вас в модели Favorite поле recipe имеет related_name='favorites', то так:
        return obj.favorites.count()
        # Если related_name не задан, то используйте: return obj.favorite_set.count()

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    
    # ТРЕБОВАНИЕ: Поиск по названию
    search_fields = ('name',)
    
    list_filter = ('measurement_unit',)

# Регистрируем остальные модели, чтобы они тоже были видны
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
