from app.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                        Shopping, Tag)
from django.contrib import admin
from users.admin import IS_EMPTY_MESSAGE


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_editable = ("measurement_unit",)
    list_filter = ("name",)
    empty_value_display = IS_EMPTY_MESSAGE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )
    list_filter = (
        "name",
        "slug",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    inlines = (RecipeIngredientInline, )
    list_display = (
        "id",
        "name",
        # "display_ingredients",
        # "display_tags",
        "author",
        "get_favorite_count",
    )
    search_fields = (
        "name",
        "author",
        "tags",
        "author__email",
        "ingredients__name",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    readonly_fields = ["get_favorite_count"]
    empty_value_display = IS_EMPTY_MESSAGE

    # def display_ingredients(self, obj):
    #     return ", ".join(
    #         [ingredient.name for ingredient in obj.ingredients.all()]
    #     )

    # display_ingredients.short_description = "Ingredients"

    # def display_tags(self, obj):
    #     return ", ".join([tag.name for tag in obj.tags.all()])
    #
    # display_tags.short_description = "Tags"

    def get_favorite_count(self, obj):
        return obj.recipe_favorite_recipes.count()

    get_favorite_count.short_description = "В избранном"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = (
        "recipe",
        "user",
    )
    list_filter = (
        "recipe",
        "user",
    )
    empty_value_display = IS_EMPTY_MESSAGE


@admin.register(Shopping)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = (
        "recipe",
        "user",
    )
    list_filter = (
        "recipe",
        "user",
    )
    empty_value_display = IS_EMPTY_MESSAGE


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "recipe",
        "ingredient",
        "amount",
    )
    search_fields = (
        "recipe",
        "ingredient",
    )
    list_editable = (
        "ingredient",
        "amount",
    )
    list_filter = ("recipe",)

    empty_value_display = IS_EMPTY_MESSAGE
