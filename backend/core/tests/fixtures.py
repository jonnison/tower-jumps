"""
Test fixtures and utilities for Tower Jumps Challenge backend tests
"""
import json
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.utils import timezone
from datetime import timedelta

# Sample test data
SAMPLE_STATES = [
    {
        "state_code": "NY",
        "name": "New York",
        "geom": MultiPolygon(
            Polygon(((-74.5, 40.5), (-74.5, 45.0), (-71.5, 45.0), (-71.5, 40.5), (-74.5, 40.5)))
        )
    },
    {
        "state_code": "CA",
        "name": "California", 
        "geom": MultiPolygon(
            Polygon(((-124.5, 32.5), (-124.5, 42.0), (-114.0, 42.0), (-114.0, 32.5), (-124.5, 32.5)))
        )
    },
    {
        "state_code": "TX",
        "name": "Texas",
        "geom": MultiPolygon(
            Polygon(((-106.5, 25.8), (-106.5, 36.5), (-93.5, 36.5), (-93.5, 25.8), (-106.5, 25.8)))
        )
    }
]

# Sample subscribers
SAMPLE_SUBSCRIBERS = [
    {"name": "John Doe"},
    {"name": "Jane Smith"},
    {"name": "Alice Johnson"},
    {"name": "Bob Wilson"},
    {"name": "Charlie Brown"}
]

# NYC area coordinates for testing
NYC_COORDINATES = [
    (-74.0059, 40.7128),  # Manhattan
    (-73.9442, 40.8176),  # Bronx
    (-73.8648, 40.8944),  # Yonkers
    (-74.0776, 40.6892),  # Brooklyn
    (-74.1502, 40.6415),  # Staten Island
]

# LA area coordinates for testing
LA_COORDINATES = [
    (-118.2437, 34.0522),  # Downtown LA
    (-118.4912, 34.0195),  # Santa Monica
    (-118.3007, 34.0736),  # West Hollywood
    (-118.1445, 34.1477),  # Pasadena
    (-118.3990, 33.9425),  # LAX area
]

def create_test_pings_for_subscriber(subscriber, state, coordinates, count=5):
    """Create test pings for a subscriber in a specific area"""
    from core.models import SubscriberPing
    
    pings = []
    base_time = timezone.now()
    
    for i in range(count):
        coord_index = i % len(coordinates)
        lng, lat = coordinates[coord_index]
        
        ping = SubscriberPing.objects.create(
            subscriber=subscriber,
            utc_time=base_time + timedelta(minutes=i*10),
            cell_type=SubscriberPing.CellType.CALL,
            geom=Point(lng, lat),
            state=state
        )
        pings.append(ping)
        
    return pings

def create_test_data():
    """Create a complete set of test data"""
    from core.models import State, Subscriber
    
    # Create states
    states = []
    for state_data in SAMPLE_STATES:
        state = State.objects.create(**state_data)
        states.append(state)
    
    # Create subscribers
    subscribers = []
    for subscriber_data in SAMPLE_SUBSCRIBERS:
        subscriber = Subscriber.objects.create(**subscriber_data)
        subscribers.append(subscriber)
    
    # Create pings for each subscriber
    all_pings = []
    
    # NYC subscriber
    nyc_pings = create_test_pings_for_subscriber(
        subscribers[0], states[0], NYC_COORDINATES, count=10
    )
    all_pings.extend(nyc_pings)
    
    # LA subscriber
    la_pings = create_test_pings_for_subscriber(
        subscribers[1], states[1], LA_COORDINATES, count=8
    )
    all_pings.extend(la_pings)
    
    # Texas subscriber with mixed coordinates
    tx_pings = create_test_pings_for_subscriber(
        subscribers[2], states[2], [(-97.7431, 30.2672)], count=6  # Austin
    )
    all_pings.extend(tx_pings)
    
    return {
        'states': states,
        'subscribers': subscribers,
        'pings': all_pings
    }

# Sample API response data for testing
SAMPLE_API_RESPONSES = {
    'subscriber_list': [
        {
            "id": 1,
            "name": "John Doe"
        },
        {
            "id": 2,
            "name": "Jane Smith"
        }
    ],
    'subscriber_detail': {
        "id": 1,
        "name": "John Doe"
    },
    'inference_result': {
        "interval_start": "2024-11-26T00:00:00Z",
        "interval_end": "2024-11-26T05:00:00Z",
        "ping_count": 5,
        "confidence_pct": "85.50",
        "method": 1,
        "subscriber": 1,
        "state": "NY",
        "pings": [
            {
                "ping_id": 1,
                "utc_time": "2024-11-26T00:00:00Z",
                "cell_type": "voice",
                "geom": "SRID=4326;POINT (-74.0059 40.7128)",
                "state": "NY"
            },
            {
                "ping_id": 2,
                "utc_time": "2024-11-26T01:00:00Z",
                "cell_type": "voice",
                "geom": "SRID=4326;POINT (-73.9442 40.8176)",
                "state": "NY"
            }
        ]
    }
}

def get_sample_api_response(response_type):
    """Get sample API response data"""
    return SAMPLE_API_RESPONSES.get(response_type, {})

# Mock data for testing algorithms
MOCK_PING_DATA = [
    {
        "ping_id": 1,
        "subscriber_id": 1,
        "utc_time": "2024-11-26T00:00:00Z",
        "cell_type": "voice",
        "longitude": -74.0059,
        "latitude": 40.7128,
        "state": "NY"
    },
    {
        "ping_id": 2,
        "subscriber_id": 1,
        "utc_time": "2024-11-26T01:00:00Z", 
        "cell_type": "voice",
        "longitude": -73.9442,
        "latitude": 40.8176,
        "state": "NY"
    },
    {
        "ping_id": 3,
        "subscriber_id": 1,
        "utc_time": "2024-11-26T02:00:00Z",
        "cell_type": "data",
        "longitude": -73.8648,
        "latitude": 40.8944,
        "state": "NY"
    }
]

def create_mock_pings_from_data(subscriber, state, ping_data):
    """Create SubscriberPing objects from mock data"""
    from core.models import SubscriberPing
    from django.utils.dateparse import parse_datetime
    
    pings = []
    for data in ping_data:
        ping = SubscriberPing.objects.create(
            subscriber=subscriber,
            utc_time=parse_datetime(data["utc_time"]),
            cell_type=data["cell_type"],
            geom=Point(data["longitude"], data["latitude"]),
            state=state
        )
        pings.append(ping)
        
    return pings

# Test constants
TEST_CONSTANTS = {
    'DEFAULT_CONFIDENCE_THRESHOLD': 50.0,
    'MAX_CLUSTERING_DISTANCE': 0.1,  # degrees
    'MIN_PING_COUNT': 1,
    'MAX_PING_COUNT': 1000,
    'TEST_TIMEOUT_SECONDS': 30,
    'PERFORMANCE_TEST_PING_COUNT': 100,
}

# Utility functions for tests
def assert_valid_location_interval(interval):
    """Assert that a LocationInterval object is valid"""
    assert interval is not None
    assert interval.ping_count >= 0
    assert 0 <= interval.confidence_pct <= 100
    assert interval.method in [1, 2]  # MAJORITY_VOTE or CLUSTERING
    assert interval.interval_start <= interval.interval_end

def assert_valid_coordinate(point):
    """Assert that a Point object has valid coordinates"""
    assert point is not None
    assert -180 <= point.x <= 180  # longitude
    assert -90 <= point.y <= 90   # latitude

def get_test_time_range(hours_back=24):
    """Get a test time range"""
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=hours_back)
    return start_time, end_time
