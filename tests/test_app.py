import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../server')))

import unittest
from server.app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to EDA Agent', response.data)

    def test_chat_get(self):
        response = self.app.get('/chat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Chat', response.data)

    def test_chat_post_missing_message(self):
        response = self.app.post('/chat', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing message field', response.data)

    def test_analyze_missing_query(self):
        response = self.app.post('/analyze', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

    def test_stats_missing_context(self):
        response = self.app.post('/stats', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

    def test_cleaning_suggestions_missing_context(self):
        response = self.app.post('/cleaning-suggestions', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

if __name__ == '__main__':
    unittest.main()
