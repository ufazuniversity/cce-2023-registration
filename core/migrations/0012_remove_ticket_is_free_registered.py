# Generated by Django 4.1.6 on 2023-03-13 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_ticket_is_free_registered"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ticket",
            name="is_free_registered",
        ),
    ]
