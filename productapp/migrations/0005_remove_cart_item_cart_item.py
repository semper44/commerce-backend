# Generated by Django 4.1.6 on 2023-03-25 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productapp', '0004_cart_owners_delete_pendingproduct'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='item',
        ),
        migrations.AddField(
            model_name='cart',
            name='item',
            field=models.TextField(default='p'),
            preserve_default=False,
        ),
    ]
