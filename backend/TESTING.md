# Backend Testing Documentation

This document describes the testing strategy and implementation for the Tower Jumps Challenge backend.

## Test Structure

The test suite is organized into several categories:

### 1. Model Tests
- **StateModelTests**: Tests for the State model
- **SubscriberModelTests**: Tests for the Subscriber model  
- **SubscriberPingModelTests**: Tests for the SubscriberPing model
- **LocationIntervalModelTests**: Tests for the LocationInterval model

### 2. Algorithm Tests
- **AlgorithmTests**: Tests for location inference algorithms
  - Majority Vote algorithm
  - Clustering algorithm
  - Algorithm registry functionality

### 3. API Tests
- **APITests**: Tests for REST API endpoints
  - Subscriber endpoints
  - State endpoints
  - Ping endpoints
  - Inference endpoints

### 4. Integration Tests
- **IntegrationTests**: End-to-end workflow tests
  - Complete data flow from ping creation to inference
  - Error handling scenarios
  - Edge cases

### 5. Performance Tests
- **PerformanceTests**: Performance and scalability tests
  - Large dataset handling
  - Algorithm performance benchmarks
  - Memory usage validation

## Running Tests

### Using Django's Test Runner

```bash
# Run all tests
uv run python manage.py test core.tests

# Run specific test class
uv run python manage.py test core.tests.StateModelTests

# Run with verbose output
uv run python manage.py test core.tests --verbosity=2

# Run with coverage
uv run coverage run --source='.' manage.py test core.tests
uv run coverage report -m
uv run coverage html
```

### Using Docker

```bash
docker-compose exec api uv run python manage.py test
```

## Test Data

### Fixtures
Test data is managed through:
- **test_fixtures.py**: Predefined test data and utility functions
- **factories.py**: Factory classes for creating test objects (optional)

### Sample Data
- **States**: New York, California, Texas with realistic boundaries
- **Subscribers**: Sample user accounts
- **Pings**: Realistic location data for NYC, LA, and Austin areas

## Test Configuration

### Settings
Tests use Django's default test settings with:
- In-memory SQLite database for speed
- Debug mode enabled
- Simplified logging configuration

### Environment Variables
```bash
DJANGO_SETTINGS_MODULE=config.settings
DATABASE_URL=sqlite:///:memory:
```

## Test Categories

### Unit Tests
Test individual components in isolation:
- Model methods and properties
- Algorithm implementations
- Utility functions

### Integration Tests
Test interaction between components:
- Database queries with ORM
- API request/response cycles
- Algorithm integration with models

### Performance Tests
Validate system performance:
- Large dataset processing
- Algorithm execution time
- Memory usage patterns

## Coverage Goals

- **Overall Coverage**: 80%+ 
- **Model Coverage**: 90%+
- **Algorithm Coverage**: 95%+
- **API Coverage**: 85%+

## Test Best Practices

### 1. Test Isolation
- Each test is independent
- Use setUp/tearDown for test data
- Clean database state between tests

### 2. Meaningful Test Names
```python
def test_subscriber_ping_creation_with_valid_data(self):
def test_majority_vote_algorithm_with_empty_dataset(self):
def test_api_returns_404_for_nonexistent_subscriber(self):
```

### 3. Test Data Management
- Use factories for consistent test data
- Create minimal data needed for each test
- Use realistic but simple coordinates

### 4. Assertion Patterns
```python
# Model assertions
self.assertEqual(subscriber.name, "Test User")
self.assertIsInstance(ping.geom, Point)

# API assertions
self.assertEqual(response.status_code, status.HTTP_200_OK)
self.assertIn('ping_count', response.data)

# Algorithm assertions
self.assertGreater(interval.confidence_pct, 0)
self.assertLessEqual(interval.confidence_pct, 100)
```

## Mock Data and Fixtures

### Geographic Data
- **NYC Area**: Manhattan, Bronx, Brooklyn coordinates
- **LA Area**: Downtown, Santa Monica, Pasadena coordinates  
- **State Boundaries**: Simplified polygons for testing

### Time Data
- Sequential timestamps for ordered testing
- Realistic time ranges for inference
- Edge cases (empty ranges, overlapping intervals)

## Debugging Tests

### Common Issues

1. **Database Errors**
   ```bash
   # Reset test database
   uv run python manage.py migrate --run-syncdb
   ```

2. **GeoDjango Issues**
   ```bash
   # Check GDAL installation
   uv run python -c "from django.contrib.gis.gdal import check_settings; check_settings()"
   ```

3. **Import Errors**
   ```bash
   # Check Python path
   uv run python -c "import sys; print(sys.path)"
   ```

### Test Debugging Tools

```python
# Add debug output
import logging
logging.basicConfig(level=logging.DEBUG)

# Print test data
print(f"Subscriber: {subscriber.__dict__}")
print(f"Pings: {list(pings.values())}")

# Use pdb for debugging
import pdb; pdb.set_trace()
```

## Continuous Integration

### GitHub Actions
```yaml
- name: Run tests
  run: |
    uv run python manage.py test --verbosity=2
    uv run coverage run --source='.' manage.py test 
    uv run coverage report --fail-under=80
```

## Performance Benchmarks

### Target Performance
- **Small Dataset** (< 10 pings): < 100ms
- **Medium Dataset** (10-100 pings): < 1s
- **Large Dataset** (100-1000 pings): < 10s

### Memory Usage
- **Maximum Memory**: 512MB per algorithm execution
- **Memory Cleanup**: Proper cleanup after each test

## Future Enhancements

1. **Property-Based Testing**: Use hypothesis for edge case discovery
2. **Load Testing**: Simulate concurrent user requests
3. **Database Performance**: Test complex spatial queries
4. **API Integration**: Test with frontend integration
5. **Deployment Testing**: Test in production-like environment

## Troubleshooting

### Common Test Failures

1. **Geographic Boundary Issues**
   - Check coordinate system (SRID=4326)
   - Validate polygon/point relationships

2. **Time Zone Issues**
   - Use timezone-aware datetime objects
   - Test with different time zones

3. **Algorithm Precision**
   - Account for floating-point precision
   - Use appropriate tolerance in assertions

### Getting Help
- Check Django documentation for testing
- Review PostGIS documentation for spatial queries
- Consult algorithm-specific documentation
