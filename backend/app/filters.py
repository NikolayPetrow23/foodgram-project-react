from app.models import Ingredient, Recipe
from django_filters import rest_framework as filters
from users.models import User

RECIPE_CHOICE = (
    (0, 'no_list'),
    (1, 'there_is_a_list')
)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.ChoiceFilter(
        choices=RECIPE_CHOICE,
        method='filter_is_favorited'
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=RECIPE_CHOICE,
        method='filter_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == '1':
            queryset = queryset.filter(
                recipe_favorite_recipes__user=user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == '1':
            queryset = queryset.filter(
                recipe_shopping_recipes__user=user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'author',
            'is_in_shopping_cart',
            'tags'
        )
