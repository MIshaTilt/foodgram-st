from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

# Use the custom user model defined in the 'users' app
User = get_user_model()

class Ingredient(models.Model):
    """Represents a cooking ingredient."""
    name = models.CharField(max_length=128, verbose_name='Name')
    measurement_unit = models.CharField(max_length=64, verbose_name='Unit')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Represents a cooking recipe."""
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='recipes',
        verbose_name='Author'
    )
    name = models.CharField(max_length=256, verbose_name='Name')
    image = models.ImageField(
        upload_to='recipes/images/', 
        verbose_name='Image'
    )
    text = models.TextField(verbose_name='Description')

    ingredients = models.ManyToManyField(
        Ingredient, 
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ingredients'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cooking Time (min)'
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Publication Date')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Intermediate model for Many-to-Many relationship between Recipe and Ingredient."""
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE, 
        related_name='ingredient_list'
    )
    ingredient = models.ForeignKey(
        Ingredient, 
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Amount'
    )

    class Meta:
        verbose_name = 'Ingredient in Recipe'
        verbose_name_plural = 'Ingredients in Recipes'


class Favorite(models.Model):
    """Stores user's favorite recipes."""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_favorite')
        ]
        verbose_name = 'Favorite'


class ShoppingCart(models.Model):
    """Stores recipes added to user's shopping cart."""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE, 
        related_name='shopping_cart'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_shopping_cart')
        ]
        verbose_name = 'Shopping Cart'


