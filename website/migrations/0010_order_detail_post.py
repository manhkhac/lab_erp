# Generated by Django 2.1.2 on 2018-12-11 08:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_order_detail_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_detail',
            name='post',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='website.Post_Product'),
            preserve_default=False,
        ),
    ]
