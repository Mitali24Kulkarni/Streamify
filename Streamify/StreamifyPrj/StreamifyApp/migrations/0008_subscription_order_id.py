# Generated by Django 4.2.7 on 2023-11-14 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StreamifyApp', '0007_alter_subscription_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
