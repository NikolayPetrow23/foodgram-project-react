import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from app.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                        Shopping, Tag)
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

            for ingredient_data in ingredients_data:
                ingredient = ingredient_data.get('ingredient')

                amount = ingredient_data.get('amount')

                RecipeIngredients.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient['id'].id,
                    amount=amount
                )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['ingredients'] = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(), many=True
        ).data

        tags_data = TagSerializer(instance.tags.all(), many=True).data
        representation['tags'] = tags_data

        return representation


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'image.{ext}'
                )
                return super().to_internal_value(data)
            except Exception as e:
                raise serializers.ValidationError(
                    "Invalid image. Failed to decode Base64 data."
                )

        return super().to_internal_value(data)


class RecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    image = Base64ImageField(required=False)
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
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.get('ingredient')
            amount = ingredient_data.get('amount')

            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=amount
            )

            recipe.tags.set(tags_data)

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
