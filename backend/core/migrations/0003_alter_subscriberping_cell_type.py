# Generated by Django 5.2.4 on 2025-07-06 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_locationinterval_alter_subscriberping_subscriber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriberping',
            name='cell_type',
            field=models.CharField(choices=[('voice', 'Voice'), ('sms', 'SMS'), ('data', 'Data')], max_length=6),
        ),
    ]
