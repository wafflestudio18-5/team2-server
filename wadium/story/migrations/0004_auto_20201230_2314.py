# Generated by Django 3.1 on 2020-12-30 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0003_auto_20201223_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='uid',
        ),
        migrations.AddField(
            model_name='story',
            name='body',
            field=models.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='story',
            name='featured_image',
            field=models.URLField(null=True),
        ),
        migrations.DeleteModel(
            name='StoryBlock',
        ),
    ]
