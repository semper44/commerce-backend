# Generated by Django 4.1.6 on 2023-04-05 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productapp', '0015_alter_cart_item_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='cartSize',
            field=models.TextField(default=0),
        ),
    ]
