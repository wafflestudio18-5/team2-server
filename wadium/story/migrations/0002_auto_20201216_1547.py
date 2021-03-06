# Generated by Django 3.1 on 2020-12-16 06:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('story', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='title',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='storyblock',
            unique_together={('story', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='storyread',
            unique_together={('story', 'user')},
        ),
    ]
