# Generated by Django 4.2.1 on 2023-05-06 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("e_voting", "0002_alter_poll_end_time_alter_poll_start_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="poll",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
    ]