import unittest
from flask import Flask
from app import app, db, bcrypt
from app.models import User
from flask_login import current_user
from dummy_data import generate_dummy, generate_teams

pw = bcrypt.generate_password_hash('pw').decode('utf-8')

class RegisterTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://localhost/maxwilen'
        cls.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            print("\n--- TESTING REGISTER ROUTES ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            print("\n--- SUCCESS TESTING REGISTER ROUTES ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

    def test_logout_success(self):
        # POST request to logout while being logged in
        self.client.post('/api/register', data=dict(
            username='test_logout',
            email='testlogout@example.com',
            team='AIK',
            password='pw',
            confirm_password='pw'
        ), follow_redirects=True)

        response = self.client.get('/api/logout')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"logout_success", response.data)

if __name__ == '__main__':
    unittest.main()
