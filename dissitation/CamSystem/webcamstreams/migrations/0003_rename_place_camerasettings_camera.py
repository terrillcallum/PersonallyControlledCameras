# Generated by Django 3.2.11 on 2022-03-22 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webcamstreams', '0002_auto_20220322_1626'),
    ]

    operations = [
        migrations.RenameField(
            model_name='camerasettings',
            old_name='place',
            new_name='Camera',
        ),
    ]