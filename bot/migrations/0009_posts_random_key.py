# Generated by Django 4.2.4 on 2024-12-07 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_telegram_users_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='random_key',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, unique=True),
        ),
    ]
