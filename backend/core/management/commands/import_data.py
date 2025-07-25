import csv

from datetime import datetime
from django.core.management.base import BaseCommand

from core.models import State, Subscriber, SubscriberPing
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'Command to import subscriber pings from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('subscriber_name', type=str, help='Subscriber name')
        parser.add_argument('csv', type=str, help='CSV file path')

    def handle(self, *args, **options):
        subscriber_name = options['subscriber_name']
        csv_path = options['csv']
        if Subscriber.objects.filter(name=subscriber_name).exists():
            return
        print(f"POPULATING NEW DATA FOR {subscriber_name}")

        subscriber = Subscriber.objects.create(name=subscriber_name)

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Assuming you have a State model with a polygon field called 'geom'

                    point = Point(float(row['Longitude']), float(row['Latitude']))
                    state = State.objects.filter(geom__contains=point).first()

                    SubscriberPing.objects.create(
                        subscriber=subscriber,
                        utc_time=datetime.strptime(row['UTCDateTime'], "%m/%d/%y %H:%M"),
                        cell_type=row['CellType'],
                        geom=point,
                        state=state
                    )
                except Exception as e:
                    self.stderr.write(f'Error processing row {row}: {e}')

        self.stdout.write(f'Subscriber Name: {subscriber_name}')
        self.stdout.write(f'CSV File Path: {csv_path}')
        self.stdout.write(f'Created Subscriber: {Subscriber.objects.all().count()}')
        self.stdout.write(f'Created Subscriber Pings: {SubscriberPing.objects.all().count()}')
