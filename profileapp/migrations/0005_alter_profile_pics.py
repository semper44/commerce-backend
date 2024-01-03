# Generated by Django 4.2.1 on 2024-01-03 01:55

from django.db import migrations, models
import profileapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('profileapp', '0004_alter_profile_blocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='pics',
            field=models.ImageField(blank=True, null=True, upload_to=profileapp.models.upload_to),
        ),
    ]