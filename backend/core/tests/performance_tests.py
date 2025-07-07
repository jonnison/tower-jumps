from django.test import TestCase, override_settings
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.utils import timezone
from datetime import timedelta

from core.models import State, Subscriber, SubscriberPing, LocationInterval
from core.algorithms import LocationInferenceModel

@override_settings(DEBUG=True)
class PerformanceTests(TestCase):
    """Performance tests for large datasets"""
    
    def setUp(self):
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        multipolygon = MultiPolygon(polygon)
        
        self.state = State.objects.create(
            state_code="NY",
            name="New York",
            geom=multipolygon
        )
        
        self.subscriber = Subscriber.objects.create(name="Performance Test User")
        
    def test_large_dataset_performance(self):
        """Test performance with larger dataset"""
        # Create 100 pings
        now = timezone.now()
        pings = []
        
        for i in range(100):
            ping = SubscriberPing.objects.create(
                subscriber=self.subscriber,
                utc_time=now + timedelta(minutes=i),
                cell_type=SubscriberPing.CellType.CALL,
                geom=Point(-74.0 + (i%10)*0.01, 40.7 + (i%10)*0.01),
                state=self.state
            )
            pings.append(ping)
            
        # Test both algorithms with timing
        import time
        
        pings_queryset = SubscriberPing.objects.filter(subscriber=self.subscriber)
        
        for method_id in [LocationInterval.Method.MAJORITY_VOTE, LocationInterval.Method.CLUSTERING]:
            algorithm = LocationInferenceModel.get(method_id)
            
            start_time = time.time()
            interval = algorithm.infer_intervals(self.subscriber, pings=pings_queryset)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Should complete within reasonable time (adjust threshold as needed)
            self.assertLess(execution_time, 10.0)  # 10 seconds max
            
            # Verify results
            self.assertEqual(interval.ping_count, 100)
            self.assertGreater(interval.confidence_pct, 0)
