# Generated by Django 5.0.1 on 2024-02-01 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_ratingoption_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingoption',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
