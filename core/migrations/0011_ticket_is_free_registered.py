# Generated by Django 4.1.6 on 2023-03-13 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_alter_order_order_id_alter_order_paid_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="is_free_registered",
            field=models.BooleanField(default=False),
        ),
    ]