# Generated by Django 4.1.2 on 2024-12-16 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_posts_random_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='statics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('static', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]