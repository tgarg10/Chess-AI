# Generated by Django 3.2.11 on 2022-03-17 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SchoolYard', '0005_auto_20220317_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='time',
            field=models.CharField(default='18:59:59', max_length=16),
        ),
        migrations.AlterField(
            model_name='history',
            name='timestamp',
            field=models.CharField(default=1647514799.187155, max_length=24),
        ),
    ]