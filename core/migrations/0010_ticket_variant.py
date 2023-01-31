# Generated by Django 4.1.5 on 2023-01-31 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_remove_ticket_type_delete_tickettype"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="variant",
            field=models.CharField(
                blank=True,
                choices=[("student", "Student"), ("other", "Other")],
                max_length=20,
                null=True,
            ),
        ),
    ]
