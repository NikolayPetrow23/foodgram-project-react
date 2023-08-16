from app.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                        Shopping, Tag)
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('is_favorited',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        source='recipe_ingredients',
        write_only=True
    )
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return instance.is_favorited.filter(
                id=request.user.id
            ).exists()
        return False

    def get_is_in_shopping_cart(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return instance.is_in_shopping_cart.filter(
                id=request.user.id
            ).exists()
        return False

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        if 'recipe_ingredients' in validated_data:
            ingredients_data = validated_data.pop('recipe_ingredients')
            RecipeIngredients.objects.filter(recipe=instance).delete()

            ingredient_objs = [
                RecipeIngredients(
                    recipe=instance,
                    ingredient_id=ingredient_data['ingredient']['id'].id,
                    amount=ingredient_data['amount']
                )
                for ingredient_data in ingredients_data
            ]

            RecipeIngredients.objects.bulk_create(ingredient_objs)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['ingredients'] = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(), many=True
        ).data

        tags_data = TagSerializer(instance.tags.all(), many=True).data
        representation['tags'] = tags_data

        return representation


class RecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author',
            'name', 'tags',
            'ingredients',
            'cooking_time',
            'text', 'image'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        # validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        ingredient_objs = [
            RecipeIngredients(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'].id,
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]

        RecipeIngredients.objects.bulk_create(ingredient_objs)

        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['ingredients'] = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data

        tags_data = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        representation['tags'] = tags_data

        return representation


class ShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopping
        fields = ('is_in_shopping_cart',)
