# Generated by Django 2.1.2 on 2018-12-06 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
