# Generated by Django 4.1.6 on 2023-03-14 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profileapp', '0004_alter_profile_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='notification',
            field=models.ManyToManyField(blank=True, related_name='productnotification', to='profileapp.productnotifications'),
        ),
    ]
