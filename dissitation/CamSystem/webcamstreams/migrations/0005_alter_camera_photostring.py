# Generated by Django 3.2.11 on 2022-03-22 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webcamstreams', '0004_auto_20220322_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='photoString',
            field=models.TextField(),
        ),
    ]
