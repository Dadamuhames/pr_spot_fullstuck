# Generated by Django 4.1 on 2023-05-22 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offers',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
