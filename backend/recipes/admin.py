from django.contrib import admin
from .models import (
    Recipe, Ingredient, Favorite, ShoppingCart, IngredientInRecipe
)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites')
    readonly_fields = ('added_in_favorites',)

    search_fields = ('name', 'author__username')

    list_filter = ('author',)
    inlines = (IngredientInline,)

    @admin.display(description='В избранном')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')

    search_fields = ('name',)

    list_filter = ('measurement_unit',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')

    search_fields = ('user__username', 'user__email', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')

    search_fields = ('user__username', 'user__email', 'recipe__name')
