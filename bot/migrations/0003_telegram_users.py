# Generated by Django 4.2.4 on 2024-11-13 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_alter_posts_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Telegram_users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(blank=True, default=None, null=True, unique=True)),
            ],
        ),
    ]