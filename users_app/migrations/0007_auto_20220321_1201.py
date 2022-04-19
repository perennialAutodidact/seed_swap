# Generated by Django 3.2 on 2022-03-21 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0006_alter_student_tuition_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='enrollment_status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='users_app.enrollmentstatus'),
        ),
        migrations.AlterField(
            model_name='student',
            name='funding_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='users_app.fundingtype'),
        ),
    ]
