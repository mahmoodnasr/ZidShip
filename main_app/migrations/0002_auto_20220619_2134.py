# Generated by Django 3.2.13 on 2022-06-19 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courier',
            old_name='date_time_div',
            new_name='date_div',
        ),
        migrations.AddField(
            model_name='courier',
            name='time_div',
            field=models.JSONField(default=dict),
        ),
    ]
