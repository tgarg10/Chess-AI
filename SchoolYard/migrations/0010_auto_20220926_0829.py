# Generated by Django 3.2.11 on 2022-09-26 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SchoolYard', '0009_auto_20220317_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='date',
            field=models.CharField(default='26 Sep 2022', max_length=16),
        ),
        migrations.AlterField(
            model_name='history',
            name='time',
            field=models.CharField(default='08:29:04', max_length=16),
        ),
        migrations.AlterField(
            model_name='history',
            name='timestamp',
            field=models.CharField(default=1664198944.319832, max_length=24),
        ),
        migrations.AlterField(
            model_name='history',
            name='winner',
            field=models.CharField(blank=True, max_length=48),
        ),
    ]
