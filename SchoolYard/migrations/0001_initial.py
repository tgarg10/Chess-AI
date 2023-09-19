# Generated by Django 3.2.11 on 2022-02-15 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=16)),
                ('time', models.CharField(max_length=16)),
                ('game_fen', models.CharField(max_length=96)),
                ('moves', models.CharField(max_length=512)),
                ('winner', models.CharField(max_length=8)),
                ('victory_condition', models.CharField(max_length=32)),
                ('computer_time_left', models.CharField(max_length=16)),
                ('player_time_left', models.CharField(max_length=16)),
            ],
        ),
    ]