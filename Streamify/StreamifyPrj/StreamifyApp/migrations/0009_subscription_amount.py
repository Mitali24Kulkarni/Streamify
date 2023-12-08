# Generated by Django 4.2.7 on 2023-11-14 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StreamifyApp', '0008_subscription_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
