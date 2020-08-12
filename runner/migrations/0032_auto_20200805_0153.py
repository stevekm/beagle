# Generated by Django 2.2.11 on 2020-08-05 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0003_jobgroupnotifier_notifier'),
        ('runner', '0031_merge_20200617_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='operatorrun',
            name='job_group_notifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notifier.JobGroupNotifier'),
        ),
        migrations.AddField(
            model_name='run',
            name='job_group_notifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notifier.JobGroupNotifier'),
        ),
    ]