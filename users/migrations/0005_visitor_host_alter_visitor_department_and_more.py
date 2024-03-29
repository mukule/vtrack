# Generated by Django 5.0.1 on 2024-01-16 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_department_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='host',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.staff'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.department'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
