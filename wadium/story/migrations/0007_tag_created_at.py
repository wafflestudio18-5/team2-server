# Generated by Django 3.1.3 on 2021-01-08 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0006_auto_20210102_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]