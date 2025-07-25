# Generated by Django 5.2.4 on 2025-07-06 20:34

import django.contrib.gis.db.models.fields
import django.contrib.postgres.indexes
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('state_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'verbose_name_plural': 'states',
                'indexes': [django.contrib.postgres.indexes.GistIndex(fields=['geom'], name='core_state_geom_ce2fd2_gist')],
            },
        ),
        migrations.CreateModel(
            name='SubscriberPing',
            fields=[
                ('ping_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('utc_time', models.DateTimeField()),
                ('cell_type', models.CharField(choices=[('call', 'Call'), ('sms', 'SMS'), ('data', 'Data')], max_length=4)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.state')),
                ('subscriber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pings', to='core.subscriber')),
            ],
            options={
                'ordering': ['-utc_time'],
                'indexes': [models.Index(fields=['utc_time'], name='core_subscr_utc_tim_f44460_idx'), models.Index(fields=['subscriber', 'utc_time'], name='core_subscr_subscri_ba654a_idx'), django.contrib.postgres.indexes.GistIndex(fields=['geom'], name='core_subscr_geom_b03154_gist')],
            },
        ),
    ]
