# Generated by Django 3.2.11 on 2022-02-15 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SchoolYard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='date',
            field=models.CharField(default='16 Feb 2022', max_length=16),
        ),
        migrations.AlterField(
            model_name='history',
            name='time',
            field=models.CharField(default='01:43:01', max_length=16),
        ),
    ]
