from django.test import TestCase
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.utils import timezone
from datetime import timedelta

from core.models import State, Subscriber, SubscriberPing, LocationInterval
from core.algorithms import LocationInferenceModel


class IntegrationTests(TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        # Create test geometry
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        multipolygon = MultiPolygon(polygon)
        
        self.state = State.objects.create(
            state_code="NY",
            name="New York",
            geom=multipolygon
        )
        
        self.subscriber = Subscriber.objects.create(name="Integration Test User")
        
    def test_complete_workflow(self):
        """Test complete workflow from ping creation to inference"""
        # Create pings over time
        now = timezone.now()
        pings = []
        
        for i in range(10):
            ping = SubscriberPing.objects.create(
                subscriber=self.subscriber,
                utc_time=now + timedelta(minutes=i*5),
                cell_type=SubscriberPing.CellType.CALL,
                geom=Point(-74.0 + i*0.005, 40.7 + i*0.005),
                state=self.state
            )
            pings.append(ping)
            
        # Test both algorithms
        for method_id in [LocationInterval.Method.MAJORITY_VOTE, LocationInterval.Method.CLUSTERING]:
            algorithm = LocationInferenceModel.get(method_id)
            
            # Run inference
            pings_queryset = SubscriberPing.objects.filter(subscriber=self.subscriber)
            interval = algorithm.infer_intervals(self.subscriber, pings=pings_queryset)
            
            # Verify results
            self.assertIsInstance(interval, LocationInterval)
            self.assertEqual(interval.subscriber, self.subscriber)
            self.assertEqual(interval.method, method_id)
            self.assertEqual(interval.ping_count, 10)
            self.assertGreater(interval.confidence_pct, 0)
            self.assertLessEqual(interval.confidence_pct, 100)
            
    def test_empty_pings_handling(self):
        """Test handling of empty ping sets"""
        # Create subscriber with no pings
        empty_subscriber = Subscriber.objects.create(name="Empty User")
        
        for method_id in [LocationInterval.Method.MAJORITY_VOTE, LocationInterval.Method.CLUSTERING]:
            algorithm = LocationInferenceModel.get(method_id)
            
            # Run inference with empty queryset
            empty_pings = SubscriberPing.objects.filter(subscriber=empty_subscriber)
            interval = algorithm.infer_intervals(empty_subscriber, pings=empty_pings)
            
            # Should handle empty case gracefully
            self.assertIsNone(interval)

