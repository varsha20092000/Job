# Generated by Django 5.1.7 on 2025-06-22 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0014_company_is_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='company_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
