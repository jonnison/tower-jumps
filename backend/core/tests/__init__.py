"""
Test suite for Tower Jumps Challenge backend core app.

This module imports all test classes to make them discoverable by Django's test runner.
"""

# Import all test classes so Django can find them
from core.tests.models_tests import *
from core.tests.algorithms_tests import *
from core.tests.endpoints_tests import *
from core.tests.integration_tests import *
from core.tests.performance_tests import *

# Make test classes available at package level
__all__ = [
    # Model tests
    'StateModelTests',
    'SubscriberModelTests', 
    'SubscriberPingModelTests',
    'LocationIntervalModelTests',
    
    # Algorithm tests
    'AlgorithmTests',
    'MajorityVoteAlgorithmTests',
    'ClusteringAlgorithmTests',
    
    # API tests
    'APITests',
    'SubscriberAPITests',
    'StateAPITests',
    'PingAPITests',
    
    # Integration tests
    'IntegrationTests',
    'WorkflowTests',
    
    # Performance tests
    'PerformanceTests',
    'ScalabilityTests',
]