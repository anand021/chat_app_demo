# Generated by Django 4.1 on 2022-11-14 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_appuser_is_admin_alter_appuser_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='full_name',
            field=models.CharField(max_length=400, null=True),
        ),
    ]
