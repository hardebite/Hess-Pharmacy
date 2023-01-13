# Generated by Django 4.1.5 on 2023-01-06 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_shippingaddress_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='info',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='info', to='store.shippingaddress'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='number',
            field=models.CharField(default=123445, max_length=200),
            preserve_default=False,
        ),
    ]
