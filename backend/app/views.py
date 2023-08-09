from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.filters import IngredientFilter, RecipeFilter
from app.generate_shopping_cart import generate_shopping_list
from app.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                        Shopping, Tag)
from app.pagination import CustomPagination
from app.permissions import IsAuthorOrReadOnly, ReadOnly
from app.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeFavoriteSerializer, RecipeSerializer,
                             TagSerializer)


class IngredientViewSet(ModelViewSet):
    """
    Чтение ингредиентов и фильтрация по названию.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    http_method_names = ('get',)
    permission_classes = (ReadOnly,)


class TagViewSet(ModelViewSet):
    """
    Чтение тегов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)
    permission_classes = (ReadOnly,)


class RecipeViewSet(ModelViewSet):
    """
    Чтение, создание, обновление рецептов.
    Создание и удаление избранного рецепта.
    Создание списка покупок из рецепта и
    удаление рецепта из списка покупок.
    Скачивание списка покупок в PDF.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    http_method_names = ('get', 'patch', 'delete', 'post')
    permission_classes_by_action = {
        'create': [permissions.IsAuthenticated],
        'update': [IsAuthorOrReadOnly],
        'destroy': [IsAuthorOrReadOnly],
        'list': [permissions.AllowAny],
        'retrieve': [permissions.AllowAny],
    }

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        elif self.action == 'favorite' or self.action == 'shopping':
            return RecipeFavoriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """
        Функция добавления и удаления рецепта в избранное.
        """
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(
                    {'detail': 'Рецепт удален из ибранного.'},
                    status=204
                )
            except Favorite.DoesNotExist:
                return Response(
                    {'detail': 'Рецепта нет в избранном.'},
                    status=404
                )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping(self, request, pk=None):
        """
        Функция добавления и удаления рецепта в списке покупок.
        """
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            shopping_obj, created = Shopping.objects.get_or_create(
                user=user,
                recipe=recipe
            )

            if not created:
                return Response(
                    {"error": "Этот рецепт уже добавлен в список покупок!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            try:
                shopping_obj = Shopping.objects.get(user=user, recipe=recipe)
                shopping_obj.delete()
                return Response(
                    {'detail': 'Рецепт удален из списка покупок.'},
                    status=204
                )
            except Favorite.DoesNotExist:
                return Response(
                    {'detail': 'Рецепта нет в списке покупок.'},
                    status=404
                )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Функция скачивания списка покупок.
        """
        user = request.user
        shop_cart = Shopping.objects.filter(user=user)

        if shop_cart:
            recipe_ids = shop_cart.values_list('recipe', flat=True)

            ingredients_data = RecipeIngredients.objects.filter(
                recipe__in=recipe_ids
            ).values_list(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).annotate(
                amount=Sum('amount')
            )

            pdf_buffer = generate_shopping_list(ingredients_data)

            response = HttpResponse(
                pdf_buffer.getvalue(),
                content_type='application/pdf'
            )
            attachment = 'attachment; filename="shopping_list.pdf"'
            response['Content-Disposition'] = attachment

            return response

        else:
            return Response(
                {'message': 'Список покупок пуст!'},
                status=status.HTTP_200_OK
            )
