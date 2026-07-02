from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

class KundliMatchAPITests(APITestCase):

    def setUp(self):
        # Create a test user and generate a JWT token for authentication
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.url = '/api/match/' # Make sure this matches your path name in urls.py
        
        # Clear cache before each test execution
        cache.clear()

        # Valid payload sample data matching your Postman structures
        self.valid_payload = {
            "male": {
                "name": "Rahul",
                "date_of_birth": "1995-05-15",
                "time_of_birth": "08:30:00",
                "latitude": 28.6139,
                "longitude": 77.2090
            },
            "female": {
                "name": "Priya",
                "date_of_birth": "1997-08-22",
                "time_of_birth": "14:15:00",
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }

    def test_match_endpoint_requires_authentication(self):
        """Test 1: Ensure requests without a valid JWT token are blocked with 401 Unauthorized"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_match_calculation(self):
        """Test 2: Ensure valid payloads return a 201 Created status and correct response schema"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['source'], 'calculated')
        self.assertIn('compatibility_score', response.data['data'])
        self.assertIn('verdict', response.data['data'])
        self.assertIn('breakdown', response.data['data'])

    def test_serializer_validation_invalid_payload(self):
        """Test 3: Ensure invalid/missing payload data triggers a 400 Bad Request via serializers"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        invalid_payload = {
            "male": {
                "name": "Rahul"
                # Missing required date, time, coordinates
            }
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_redis_caching_mechanism(self):
        """Test 4: Ensure the second matching request hit returns instantly from the cache layer"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        # First call hits the database/engine calculations
        first_response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(first_response.data['source'], 'calculated')

        # Second identical call must fetch directly from the Redis cache layer
        second_response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data['source'], 'cache')