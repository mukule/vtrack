# Generated by Django 5.0.1 on 2024-02-01 10:45

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_visitor_purpose_of_visit'),
    ]

    operations = [
        migrations.CreateModel(
            name='RatingOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.visitor')),
                ('rate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.ratingoption')),
            ],
        ),
    ]
