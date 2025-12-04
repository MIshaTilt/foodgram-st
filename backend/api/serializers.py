import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer as DjoserUserSerializer

# Импортируем модели из старых приложений
from users.models import User, Subscription
from recipes.models import Recipe, Ingredient, IngredientInRecipe, Favorite, ShoppingCart

# --- Utils ---
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

# --- User Serializers ---

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

class CustomUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

# --- Recipe Serializers ---

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(source='ingredient_list', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
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
        fields = ('id', 'ingredients', 'image', 'name', 'text', 'cooking_time', 'author')

    def validate(self, data):
        if self.instance and 'ingredients' not in data:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно для заполнения при обновлении."}
            )
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Нужен хотя бы один ингредиент.")
        
        ingredients_list = []
        for item in value:
            ingredient_id = item['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError("Ингредиенты не должны повторяться.")
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(f"Ингредиента с id {ingredient_id} не существует.")
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

# --- Subscription Serializer (Placed last because it uses RecipeMinifiedSerializer) ---

class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                pass
        return RecipeMinifiedSerializer(recipes, many=True, context=self.context).data
