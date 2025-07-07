import factory
from factory import fuzzy
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.utils import timezone
from datetime import timedelta

from core.models import State, Subscriber, SubscriberPing


class StateFactory(factory.django.DjangoModelFactory):
    """Factory for creating State instances"""
    
    class Meta:
        model = State
        
    state_code = factory.Sequence(lambda n: f"S{n:02d}")
    name = factory.Faker('state')
    geom = factory.LazyFunction(
        lambda: MultiPolygon(
            Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        )
    )


class SubscriberFactory(factory.django.DjangoModelFactory):
    """Factory for creating Subscriber instances"""
    
    class Meta:
        model = Subscriber
        
    name = factory.Faker('name')


class SubscriberPingFactory(factory.django.DjangoModelFactory):
    """Factory for creating SubscriberPing instances"""
    
    class Meta:
        model = SubscriberPing
        
    subscriber = factory.SubFactory(SubscriberFactory)
    utc_time = factory.LazyFunction(timezone.now)
    cell_type = fuzzy.FuzzyChoice(SubscriberPing.CellType.choices, getter=lambda c: c[0])
    geom = factory.LazyFunction(
        lambda: Point(
            fuzzy.FuzzyFloat(-180, 180).fuzz(),
            fuzzy.FuzzyFloat(-90, 90).fuzz()
        )
    )
    state = factory.SubFactory(StateFactory)
    
    @factory.post_generation
    def set_utc_time_sequence(self, create, extracted, **kwargs):
        """Set sequential UTC times for ordered pings"""
        if extracted:
            self.utc_time = timezone.now() + timedelta(minutes=extracted)
            if create:
                self.save()


class SubscriberPingBatchFactory(factory.django.DjangoModelFactory):
    """Factory for creating multiple SubscriberPing instances for the same subscriber"""
    
    class Meta:
        model = SubscriberPing
        
    subscriber = factory.SubFactory(SubscriberFactory)
    cell_type = SubscriberPing.CellType.CALL
    state = factory.SubFactory(StateFactory)
    
    @classmethod
    def create_batch_for_subscriber(cls, subscriber, count=5, **kwargs):
        """Create a batch of pings for a specific subscriber"""
        pings = []
        base_time = timezone.now()
        
        for i in range(count):
            ping = cls.create(
                subscriber=subscriber,
                utc_time=base_time + timedelta(minutes=i*10),
                geom=Point(-74.0 + i*0.01, 40.7 + i*0.01),
                **kwargs
            )
            pings.append(ping)
            
        return pings
