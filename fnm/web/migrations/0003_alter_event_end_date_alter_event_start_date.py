# Generated by Django 5.2 on 2025-04-06 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_event_eventprogram_galleryimage_generaleventinfo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]
