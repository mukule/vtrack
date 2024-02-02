# Generated by Django 5.0.1 on 2024-02-02 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_alter_ratingoption_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='visitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='users.visitor'),
        ),
    ]
