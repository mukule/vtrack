# Generated by Django 5.0.1 on 2024-01-24 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_visitortag'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='tag_number',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
    ]
