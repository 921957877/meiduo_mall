# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-05-26 18:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_goodsvisitcount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skuspecification',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='goods.SKU', verbose_name='sku'),
        ),
    ]
