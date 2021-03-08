# Generated by Django 3.1.5 on 2021-03-06 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20210304_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Director'), (2, 'Manager'), (3, 'Team_Lead'), (4, 'Member')], null=True),
        ),
    ]