# Generated by Django 4.1.5 on 2023-01-30 15:16

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_rename_datetime_order_created_order_updated"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="description",
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
