# Generated by Django 2.1.2 on 2018-11-14 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post_product',
            name='expire_visable_page_home',
        ),
        migrations.RemoveField(
            model_name='service',
            name='day_visable_page_home',
        ),
        migrations.AddField(
            model_name='post_product',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
