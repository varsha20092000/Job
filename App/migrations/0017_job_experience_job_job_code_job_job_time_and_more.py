# Generated by Django 5.1.7 on 2025-06-23 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0016_company_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='experience',
            field=models.CharField(choices=[('1-2 Year', '1-2 Year'), ('2-5 Year', '2-5 Year'), ('5+ Year', '5+ Year')], default='1-2 Year', max_length=50),
        ),
        migrations.AddField(
            model_name='job',
            name='job_code',
            field=models.CharField(default=12, max_length=20, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='job',
            name='job_time',
            field=models.CharField(choices=[('Full Time', 'Full Time'), ('Part Time', 'Part Time')], default='Full Time', max_length=50),
        ),
        migrations.AddField(
            model_name='job',
            name='short_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='work_hour',
            field=models.PositiveIntegerField(default=2),
        ),
    ]
