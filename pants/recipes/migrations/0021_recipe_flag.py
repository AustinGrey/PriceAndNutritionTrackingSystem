# Generated by Django 3.0.2 on 2020-03-10 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_recipeflag'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='flag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.RecipeFlag'),
        ),
    ]