# Generated by Django 4.1.5 on 2023-02-02 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_ticket_includes_dinner"),
    ]

    operations = [
        migrations.CreateModel(
            name="MealPreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("allergies", models.TextField(blank=True, null=True)),
                (
                    "special_request",
                    models.TextField(
                        blank=True,
                        help_text="E.g halal, kosher, vegetarian etc.",
                        null=True,
                    ),
                ),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT, to="core.order"
                    ),
                ),
            ],
        ),
    ]