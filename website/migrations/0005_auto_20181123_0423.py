# Generated by Django 2.1.2 on 2018-11-23 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_post_product_bought'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.CharField(default='a', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order_detail',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='id_card',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='name_shop',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='phone',
            field=models.CharField(max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(choices=[('1', 'Success'), ('0', 'Cancel'), ('2', 'In Process'), ('3', 'Packing'), ('4', 'Transporting')], max_length=1),
        ),
        migrations.AlterField(
            model_name='order_detail',
            name='state',
            field=models.CharField(choices=[('1', 'Success'), ('0', 'Cancel'), ('2', 'In Process'), ('3', 'Packing'), ('4', 'Transporting')], max_length=1),
        ),
    ]
