# Generated by Django 4.2.4 on 2024-11-13 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_telegram_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='category',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='posts',
            name='category_pod',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]