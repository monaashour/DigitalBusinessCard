# Generated by Django 4.2.8 on 2023-12-17 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_remove_card_id_card_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='user',
            new_name='owner',
        ),
    ]