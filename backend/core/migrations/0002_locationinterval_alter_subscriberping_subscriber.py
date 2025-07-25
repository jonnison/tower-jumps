# Generated by Django 5.2.4 on 2025-07-06 20:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationInterval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interval_start', models.DateTimeField()),
                ('interval_end', models.DateTimeField()),
                ('confidence_pct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('method', models.PositiveSmallIntegerField(choices=[(1, 'Majority vote'), (2, 'Clustering + smoothing'), (3, 'Bayesian HMM')])),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='subscriberping',
            name='subscriber',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pings', to='core.subscriber'),
        ),
    ]
