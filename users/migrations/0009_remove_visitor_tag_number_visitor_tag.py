# Generated by Django 5.0.1 on 2024-01-24 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_visitor_tag_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitor',
            name='tag_number',
        ),
        migrations.AddField(
            model_name='visitor',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.visitortag'),
        ),
    ]
