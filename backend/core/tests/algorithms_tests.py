from django.forms import ValidationError
from django.test import TestCase
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.utils import timezone
from datetime import timedelta

from core.models import State, Subscriber, SubscriberPing, LocationInterval
from core.algorithms import LocationInferenceModel
from core.algorithms.majority_vote import MajorityVoteModel
from core.algorithms.clustering import ClusteringModel

class AlgorithmTests(TestCase):
    """Test cases for location inference algorithms"""
    
    def setUp(self):
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        multipolygon = MultiPolygon(polygon)
        
        self.state = State.objects.create(
            state_code="NY",
            name="New York",
            geom=multipolygon
        )
        
        self.subscriber = Subscriber.objects.create(name="Test User")
        
        # Create test pings
        now = timezone.now()
        self.pings = []
        for i in range(5):
            ping = SubscriberPing.objects.create(
                subscriber=self.subscriber,
                utc_time=now + timedelta(minutes=i*10),
                cell_type=SubscriberPing.CellType.CALL,
                geom=Point(-74.0 + i*0.01, 40.7 + i*0.01),
                state=self.state
            )
            self.pings.append(ping)
            
    def test_algorithm_registry(self):
        """Test that algorithms are properly registered"""
        # Check that algorithms are registered
        self.assertIn(LocationInterval.Method.MAJORITY_VOTE, LocationInferenceModel._registry)
        self.assertIn(LocationInterval.Method.CLUSTERING, LocationInferenceModel._registry)
        
    def test_get_algorithm(self):
        """Test getting algorithm by method ID"""
        majority_vote = LocationInferenceModel.get(LocationInterval.Method.MAJORITY_VOTE.value)
        clustering = LocationInferenceModel.get(LocationInterval.Method.CLUSTERING.value)
        
        self.assertIsInstance(majority_vote, MajorityVoteModel)
        self.assertIsInstance(clustering, ClusteringModel)
        
    def test_majority_vote_algorithm(self):
        """Test majority vote algorithm"""
        algorithm = MajorityVoteModel()
        
        # Test with our test pings
        pings_queryset = SubscriberPing.objects.filter(subscriber=self.subscriber)
        interval = algorithm.infer_intervals(self.subscriber, pings=pings_queryset)
        
        self.assertIsInstance(interval, LocationInterval)
        self.assertEqual(interval.subscriber, self.subscriber)
        self.assertEqual(interval.method, LocationInterval.Method.MAJORITY_VOTE)
        self.assertEqual(interval.ping_count, 5)
        
    def test_clustering_algorithm(self):
        """Test clustering algorithm"""
        algorithm = ClusteringModel()
        
        # Test with our test pings
        pings_queryset = SubscriberPing.objects.filter(subscriber=self.subscriber)
        interval = algorithm.infer_intervals(self.subscriber, pings=pings_queryset)
        
        self.assertIsInstance(interval, LocationInterval)
        self.assertEqual(interval.subscriber, self.subscriber)
        self.assertEqual(interval.method, LocationInterval.Method.CLUSTERING)

