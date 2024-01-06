# Generated by Django 3.2.13 on 2023-01-17 19:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("route_manager", "0021_auto_20220929_2047"),
    ]

    operations = [
        migrations.AddField(
            model_name="entry",
            name="expiration",
            field=models.DateTimeField(default="9999-12-31 00:00Z"),
        ),
        migrations.AddField(
            model_name="entry",
            name="expiration_reason",
            field=models.CharField(
                blank=True, help_text="Optional reason for the expiration", max_length=200, null=True
            ),
        ),
        migrations.AddField(
            model_name="entry",
            name="when",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="entry",
            name="who",
            field=models.CharField(default="Unknown", max_length=30, verbose_name="Username"),
        ),
        migrations.AddField(
            model_name="historicalentry",
            name="expiration",
            field=models.DateTimeField(default="9999-12-31 00:00Z"),
        ),
        migrations.AddField(
            model_name="historicalentry",
            name="expiration_reason",
            field=models.CharField(
                blank=True, help_text="Optional reason for the expiration", max_length=200, null=True
            ),
        ),
        migrations.AddField(
            model_name="historicalentry",
            name="when",
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalentry",
            name="who",
            field=models.CharField(default="Unknown", max_length=30, verbose_name="Username"),
        ),
        migrations.DeleteModel(
            name="History",
        ),
    ]
