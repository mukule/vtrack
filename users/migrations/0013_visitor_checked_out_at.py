# Generated by Django 5.0.1 on 2024-01-24 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_visitor_otp_visitor_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='checked_out_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
