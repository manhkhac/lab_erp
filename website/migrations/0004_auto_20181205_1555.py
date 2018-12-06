# Generated by Django 2.1.2 on 2018-12-05 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20181205_0844'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='consider',
        ),
        migrations.AlterField(
            model_name='product',
            name='detail',
            field=models.TextField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_activity',
            field=models.BooleanField(default=True),
        ),
    ]