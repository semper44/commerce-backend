# Generated by Django 4.1.6 on 2023-04-27 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productapp', '0016_cart_cartsize'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='reference',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
