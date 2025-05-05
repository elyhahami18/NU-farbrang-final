import unittest
from app import app

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_status_code(self):
        """Test that homepage loads successfully"""
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)
    
    def test_ask_route_requires_question(self):
        """Test that /ask route requires a question"""
        result = self.app.post('/ask', json={})
        self.assertEqual(result.status_code, 400)
    
if __name__ == '__main__':
    unittest.main() 