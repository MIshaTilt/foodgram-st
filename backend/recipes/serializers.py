from rest_framework import serializers

from recipes.models import Recipe, Ingredient, IngredientInRecipe, Favorite, \
    ShoppingCart
from users.serializers import CustomUserSerializer, \
    Base64ImageField

# --- Ingredient Serializers ---


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

# --- Recipe Serializers ---


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)

    ingredients = IngredientInRecipeSerializer(
        source='ingredient_list', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientInRecipeSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'image', 'name',
                  'text', 'cooking_time', 'author')

    def validate(self, data):
        # Проверка: если мы обновляем рецепт (self.instance не None),
        # то поле 'ingredients' должно обязательно присутствовать в данных.
        if self.instance and 'ingredients' not in data:
            raise serializers.ValidationError(
                {"ingredients": (
                    "Это поле обязательно для заполнения при обновлении."
                )}
            )
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Нужен хотя бы один ингредиент.")

        ingredients_list = []
        for item in value:
            ingredient_id = item['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    "Ингредиенты не должны повторяться.")

            # ДОБАВЛЕНО: Проверка существования ингредиента
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f"Ингредиента с id {ingredient_id} не существует.")

            ingredients_list.append(ingredient_id)
        return value

    def create_ingredients(self, ingredients, recipe):

        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)

        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        super().update(instance, validated_data)

        if ingredients_data:
            instance.ingredients.clear()
            self.create_ingredients(ingredients_data, instance)
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data
