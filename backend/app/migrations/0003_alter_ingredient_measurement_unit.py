# Generated by Django 3.2.3 on 2023-07-29 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(choices=[('грамм', 'Грамм'), ('кг', 'Килограмм')], default='кг', max_length=8),
        ),
    ]
