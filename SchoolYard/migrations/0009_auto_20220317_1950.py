# Generated by Django 3.2.11 on 2022-03-17 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SchoolYard', '0008_auto_20220317_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='time',
            field=models.CharField(default='19:50:59', max_length=16),
        ),
        migrations.AlterField(
            model_name='history',
            name='timestamp',
            field=models.CharField(default=1647517859.284905, max_length=24),
        ),
        migrations.AlterField(
            model_name='history',
            name='winner',
            field=models.CharField(blank=True, default='White', max_length=48),
        ),
    ]