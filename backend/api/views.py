from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

# Импорты моделей
from recipes.models import Recipe, Ingredient, Favorite, ShoppingCart, IngredientInRecipe
from users.models import User, Subscription

# Импорты из текущего приложения api
from .serializers import (
    IngredientSerializer, RecipeListSerializer, RecipeCreateSerializer,
    RecipeMinifiedSerializer, CustomUserSerializer,
    AvatarSerializer, SubscriptionSerializer
)
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['put', 'delete'], 
            permission_classes=[permissions.IsAuthenticated], 
            url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], 
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if user == author:
                return Response({'error': 'Cannot subscribe to yourself'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({'error': 'Already subscribed'},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(user=user, author=author)
            if not subscription.exists():
                return Response(
                    {'error': 'Вы не были подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeListSerializer

    def add_to(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response({'error': 'Recipe already added'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if not obj.exists():
            return Response(
                {'error': 'Рецепт не найден в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        return self.delete_from(ShoppingCart, request.user, pk)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = "Shopping List:\n\n"
        for item in ingredients:
            shopping_list += (
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['amount']}\n"
            )

        filename = "shopping_list.txt"
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        link = request.build_absolute_uri(f'/recipes/{recipe.id}')
        return Response({'short-link': link}, status=status.HTTP_200_OK)