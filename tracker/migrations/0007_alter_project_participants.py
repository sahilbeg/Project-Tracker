# Generated by Django 4.2.17 on 2024-12-12 18:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0006_project_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='participants',
            field=models.ManyToManyField(related_name='project_participants', to=settings.AUTH_USER_MODEL),
        ),
    ]
