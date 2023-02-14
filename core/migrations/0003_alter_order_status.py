# Generated by Django 4.1.6 on 2023-02-10 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_order_order_id_alter_order_paid_amount_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("APPROVED", "Complete"),
                    ("CANCELED", "Cancelled"),
                    ("REFUNDED", "Refunded"),
                ],
                default="pending",
                max_length=12,
            ),
        ),
    ]