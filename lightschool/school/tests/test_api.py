import json
from django.test import TestCase, Client
from django.urls import reverse

class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_lessons(self):
        response = self.client.get('/api/lessons/?subject=math&grade=1&locale=en')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['subject'], 'math')
        self.assertEqual(data['grade'], 1)

    def test_api_progress(self):
        # Set
        response = self.client.post('/api/progress/set/', {
            'subject': 'math',
            'grade': 1,
            'unitId': 'add_basics',
            'status': 'completed',
            'score': 80
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Get
        response = self.client.get('/api/progress/get/?subject=math&grade=1')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('add_basics', data)

    def test_api_tutor(self):
        response = self.client.post('/api/tutor/', {
            'message': 'What is addition?',
            'subject': 'math',
            'grade': 1,
            'locale': 'en'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('reply', data)
        self.assertIn('source', data)