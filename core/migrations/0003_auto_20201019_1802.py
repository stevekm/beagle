# Generated by Django 2.2.11 on 2020-10-19 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_userregistrationrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregistrationrequest',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]