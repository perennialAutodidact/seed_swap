# Generated by Django 4.0.4 on 2022-05-19 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barters_app', '0007_remove_producebarter_plantbarter_ptr_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barter',
            name='will_trade_for',
            field=models.CharField(blank=True, max_length=255, verbose_name='will trade for'),
        ),
    ]
