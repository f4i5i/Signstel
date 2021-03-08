# Generated by Django 3.1.5 on 2021-03-04 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_customuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Manager'), (2, 'Team_Lead'), (3, 'Member')], null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
