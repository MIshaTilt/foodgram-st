from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet as DjoserUserViewSet

from users.models import User, Subscription
from users.serializers import CustomUserSerializer, AvatarSerializer, SubscriptionSerializer, TokenCreateSerializer

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6

class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['put', 'delete'], permission_classes=[permissions.IsAuthenticated], url_path='me/avatar')
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
        serializer = SubscriptionSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if user == author:
                return Response({'error': 'Cannot subscribe to yourself'}, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({'error': 'Already subscribed'}, status=status.HTTP_400_BAD_REQUEST)
            
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        

class TokenCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Ищем пользователя по email
        user = User.objects.filter(email=email).first()

        # Если пользователя нет или пароль не подходит
        if user is None or not user.check_password(password):
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Генерируем AccessToken (JWT)
        token = AccessToken.for_user(user)

        # Возвращаем в формате, который требует ТЗ
        return Response({'auth_token': str(token)}, status=status.HTTP_200_OK)
    
class TokenLogoutView(APIView):
    # Разрешаем доступ всем. Если токена нет — просто вернем 204.
    permission_classes = (AllowAny,) 

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)

