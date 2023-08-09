# Generated by Django 3.2.3 on 2023-08-07 16:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0012_remove_shopping_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favorite_recipes', to='app.recipe'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_favorite_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shopping',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_shopping_recipes', to='app.recipe'),
        ),
        migrations.AlterField(
            model_name='shopping',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_shopping_recipes', to=settings.AUTH_USER_MODEL),
        ),
    ]
