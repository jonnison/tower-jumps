from django.test import TestCase
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.utils import timezone
from datetime import timedelta

from core.models import State, Subscriber, SubscriberPing


class StateModelTests(TestCase):
    """Test cases for State model"""
    
    def setUp(self):
        # Create a simple polygon for testing
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        self.multipolygon = MultiPolygon(polygon)
        
    def test_state_creation(self):
        """Test creating a state with valid data"""
        state = State.objects.create(
            state_code="NY",
            name="New York",
            geom=self.multipolygon
        )
        self.assertEqual(state.state_code, "NY")
        self.assertEqual(state.name, "New York")
        self.assertEqual(str(state), "New York")
        
    def test_state_str_representation(self):
        """Test string representation of state"""
        state = State.objects.create(
            state_code="CA",
            name="California",
            geom=self.multipolygon
        )
        self.assertEqual(str(state), "California")


class SubscriberModelTests(TestCase):
    """Test cases for Subscriber model"""
    
    def test_subscriber_creation(self):
        """Test creating a subscriber"""
        subscriber = Subscriber.objects.create(name="John Doe")
        self.assertEqual(subscriber.name, "John Doe")
        self.assertTrue(subscriber.id)
        
    def test_subscriber_str_representation(self):
        """Test string representation of subscriber"""
        subscriber = Subscriber.objects.create(name="Jane Smith")
        self.assertEqual(str(subscriber), str(subscriber.id))
        
    def test_subscriber_without_name(self):
        """Test creating subscriber without name"""
        subscriber = Subscriber.objects.create()
        self.assertEqual(subscriber.name, "")


class SubscriberPingModelTests(TestCase):
    """Test cases for SubscriberPing model"""
    
    def setUp(self):
        # Create test data
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        multipolygon = MultiPolygon(polygon)
        
        self.state = State.objects.create(
            state_code="NY",
            name="New York",
            geom=multipolygon
        )
        
        self.subscriber = Subscriber.objects.create(name="Test User")
        
    def test_subscriber_ping_creation(self):
        """Test creating a subscriber ping"""
        ping = SubscriberPing.objects.create(
            subscriber=self.subscriber,
            utc_time=timezone.now(),
            cell_type=SubscriberPing.CellType.CALL,
            geom=Point(-74.0, 40.7),  # NYC coordinates
            state=self.state
        )
        
        self.assertEqual(ping.subscriber, self.subscriber)
        self.assertEqual(ping.cell_type, SubscriberPing.CellType.CALL)
        self.assertEqual(ping.state, self.state)
        self.assertIsNotNone(ping.geom)
        
    def test_subscriber_ping_str_representation(self):
        """Test string representation of subscriber ping"""
        now = timezone.now()
        ping = SubscriberPing.objects.create(
            subscriber=self.subscriber,
            utc_time=now,
            cell_type=SubscriberPing.CellType.SMS,
            geom=Point(-74.0, 40.7),
            state=self.state
        )
        
        expected = f"{self.subscriber.id}@{now:%F %T}"
        self.assertEqual(str(ping), expected)
        
    def test_subscriber_ping_cell_type_choices(self):
        """Test cell type choices"""
        # Test all cell type choices
        for cell_type, _ in SubscriberPing.CellType.choices:
            ping = SubscriberPing.objects.create(
                subscriber=self.subscriber,
                utc_time=timezone.now(),
                cell_type=cell_type,
                geom=Point(-74.0, 40.7),
                state=self.state
            )
            self.assertEqual(ping.cell_type, cell_type)
            
    def test_subscriber_ping_ordering(self):
        """Test that pings are ordered by utc_time descending"""
        now = timezone.now()
        
        # Create pings with different times
        ping1 = SubscriberPing.objects.create(
            subscriber=self.subscriber,
            utc_time=now - timedelta(hours=2),
            cell_type=SubscriberPing.CellType.CALL,
            geom=Point(-74.0, 40.7),
            state=self.state
        )
        
        ping2 = SubscriberPing.objects.create(
            subscriber=self.subscriber,
            utc_time=now - timedelta(hours=1),
            cell_type=SubscriberPing.CellType.SMS,
            geom=Point(-74.1, 40.8),
            state=self.state
        )
        
        ping3 = SubscriberPing.objects.create(
            subscriber=self.subscriber,
            utc_time=now,
            cell_type=SubscriberPing.CellType.DATA,
            geom=Point(-74.2, 40.9),
            state=self.state
        )
        
        pings = list(SubscriberPing.objects.all())
        self.assertEqual(pings[0], ping3)  # Most recent first
        self.assertEqual(pings[1], ping2)
        self.assertEqual(pings[2], ping1)  # Oldest last
