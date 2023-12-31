from app.validators import validate_hex
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class Ingredient(models.Model):
    class Units(models.TextChoices):
        gram = 'грамм', _('Грамм')
        kilogram = 'кг', _('Килограмм')

    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(
        max_length=8,
        default=Units.kilogram,
        choices=Units.choices
    )

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}."

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        default=1,
        validators=(
            validators.MinValueValidator(
                1,
                message="Количество должно быть больше нуля."),
            validators.MaxValueValidator(
                10000,
                message="Количество не должно быть больше 10000 грамм."
            )
        ),
        verbose_name="Количество",
    )

    def __str__(self):
        return f'В рецепте {self.recipe} есть ингредиент {self.ingredient}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique ingredient"
            )
        ]


class Tag(models.Model):
    name = models.CharField(max_length=128)
    color = models.CharField(max_length=16, validators=[validate_hex])
    slug = models.SlugField(unique=True, max_length=60)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    name = models.CharField(max_length=128)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_user'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        default=None,
        blank=True
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredients,
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
    )
    is_favorited = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        blank=True,
        through='Favorite'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_recipes',
        blank=True,
        through='Shopping'
    )
    cooking_time = models.PositiveIntegerField(
        validators=(
            validators.MinValueValidator(
                1,
                message="Время приготовления должно быть больше нуля."
            ),
            validators.MaxValueValidator(
                600,
                message="Время приготовления не "
                        "должно быть больше десяти часов."
            )
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ("-id",)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorite_recipes'
    )
    is_favorited = models.BooleanField(default=False)

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class Shopping(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_recipes'
    )
    is_in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
