from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta

from core.models import State, Subscriber, SubscriberPing, LocationInterval

class APITests(APITestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
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
        for i in range(3):
            ping = SubscriberPing.objects.create(
                subscriber=self.subscriber,
                utc_time=now + timedelta(minutes=i*10),
                cell_type=SubscriberPing.CellType.CALL,
                geom=Point(-74.0 + i*0.01, 40.7 + i*0.01),
                state=self.state
            )
            self.pings.append(ping)
            
    def test_get_subscribers(self):
        """Test GET /api/subscribers/"""
        url = reverse('subscriber-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test User')
        
    def test_get_subscriber_detail(self):
        """Test GET /api/subscribers/{id}/"""
        url = reverse('subscriber-detail', kwargs={'pk': self.subscriber.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test User')
        
    def test_subscriber_infer_endpoint(self):
        """Test GET /api/subscribers/{id}/infer/"""
        url = reverse('subscriber-infer', kwargs={'pk': self.subscriber.id})
        response = self.client.get(url, {
            'model_id': LocationInterval.Method.MAJORITY_VOTE
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ping_count', response.data)
        self.assertIn('confidence_pct', response.data)
        self.assertIn('method', response.data)
        self.assertIn('pings', response.data)
        
    def test_subscriber_infer_with_time_filter(self):
        """Test subscriber inference with time filtering"""
        url = reverse('subscriber-infer', kwargs={'pk': self.subscriber.id})
        
        # Test with time range that includes all pings
        start_time = timezone.now() - timedelta(hours=1)
        end_time = timezone.now() + timedelta(hours=1)
        
        response = self.client.get(url, {
            'model_id': LocationInterval.Method.MAJORITY_VOTE,
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['pings']), 3)
        
    def test_subscriber_infer_with_clustering(self):
        """Test subscriber inference with clustering algorithm"""
        url = reverse('subscriber-infer', kwargs={'pk': self.subscriber.id})
        response = self.client.get(url, {
            'model_id': LocationInterval.Method.CLUSTERING.value
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['method'], LocationInterval.Method.CLUSTERING.value)

    def test_subscriber_infer_invalid_model(self):
        """Test subscriber inference with invalid model ID"""
        url = reverse('subscriber-infer', kwargs={'pk': self.subscriber.id})
        response = self.client.get(url, {
            'model_id': 'invalid'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_subscriber_infer_nonexistent_subscriber(self):
        """Test inference for non-existent subscriber"""
        url = reverse('subscriber-infer', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_states(self):
        """Test GET /api/states/"""
        url = reverse('state-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'New York')
        
    def test_subscriber_name_filter(self):
        """Test filtering subscribers by name"""
        # Create another subscriber
        Subscriber.objects.create(name="Another User")
        
        url = reverse('subscriber-list')
        response = self.client.get(url, {'name': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test User')

