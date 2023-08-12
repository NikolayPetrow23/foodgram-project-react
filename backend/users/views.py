from app.pagination import CustomPagination
from app.permissions import IsOwnerOrStaffOrReadOnly
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User
from users.serializers import (CustomUserResetPassword, CustomUserSerializer,
                               FollowSerializer, SignUpUserSerializer)


class FollowViewSet(viewsets.ModelViewSet):
    """
    Чтение подписок текущего пользователя.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = CustomPagination
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        review = Follow.objects.filter(user=self.request.user)
        return review

    def get_serializer_context(self):
        context = super(FollowViewSet, self).get_serializer_context()
        followers = Follow.objects.all()
        context["follow"] = followers
        return context


class CustomUserViewSet(UserViewSet):
    """
    Регистрация, чтение пользователей.
    Создает подписку на пользователя.
    """
    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = CustomUserSerializer
    permission_classes = (IsOwnerOrStaffOrReadOnly,)
    http_method_names = ('get', 'post', 'delete')
    lookup_field = 'id'
    permission_classes_by_action = {
        'create': [permissions.AllowAny],
        'destroy': [permissions.IsAdminUser],
        'list': [permissions.IsAdminUser],
        'retrieve': [permissions.AllowAny],
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return SignUpUserSerializer
        elif self.action == 'subscribe':
            return FollowSerializer
        return CustomUserSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """
        Функция подписки на пользователя.
        """
        target_user = get_object_or_404(User, pk=id)
        current_user = request.user

        if request.method == "POST":
            if current_user.id == int(id):
                return Response(
                    {"error": "Вы не можете подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription, created = Follow.objects.get_or_create(
                user=current_user,
                author=target_user
            )

            if not created:
                return Response(
                    {"error": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            follow_relationship = Follow.objects.filter(
                user=current_user,
                author=target_user
            )

            if follow_relationship.exists():
                follow_relationship.delete()
                return Response(
                    {"message": "Вы отписались от пользователя."},
                    status=status.HTTP_204_NO_CONTENT,
                )

            return Response(
                {"error": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomPasswordChangeView(APIView):
    """
    Изменение текущего пороля.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserResetPassword
    http_method_names = ('post',)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(current_password):
            raise PermissionDenied('Invalid password')

        user.set_password(new_password)
        user.save()

        return Response(
            {'message': 'Пороль успешно изменен'},
            status=status.HTTP_200_OK
        )
