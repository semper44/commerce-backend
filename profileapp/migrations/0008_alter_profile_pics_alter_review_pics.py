# Generated by Django 4.2.1 on 2024-01-19 22:05

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profileapp', '0007_alter_profile_pics_alter_review_pics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='pics',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='review',
            name='pics',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]