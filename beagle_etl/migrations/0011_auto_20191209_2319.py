# Generated by Django 2.2.2 on 2019-12-09 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beagle_etl', '0010_auto_20191205_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='callback',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
