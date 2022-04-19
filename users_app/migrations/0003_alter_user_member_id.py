# Generated by Django 3.2 on 2022-03-15 18:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0002_auto_20220315_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='member_id',
            field=models.UUIDField(default=uuid.uuid1, editable=False, unique=True),
        ),
    ]
