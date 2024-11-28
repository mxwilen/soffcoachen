import unittest
from flask import Flask
from app import app, db, bcrypt
from app.models import User
from flask_login import current_user
from dummy_data import generate_dummy, generate_teams

pw = bcrypt.generate_password_hash('pw').decode('utf-8')

class LoginTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://localhost/maxwilen'
        cls.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            print("\n--- TESTING LOGIN ROUTES ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

            # Create a test user
            cls.user = User(username="testing", 
                            email='test@example.com', 
                            password=pw)
            db.session.add(cls.user)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            print("\n--- SUCCESS TESTING LOGIN ROUTES ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

    def test_login_success(self):
        # POST request to login
        response = self.client.post('/api/login', data=dict(
            email='test@example.com',
            password='pw',
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"login_success", response.data)

    def test_login_failure(self):
        # POST request with wrong password
        response = self.client.post('/api/login', data=dict(
            email='test@example.com',
            password='wrongpassword',
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Credentials don't match", response.data)

    def test_login_no_user(self):
        # POST request with non-existing user
        response = self.client.post('/api/login', data=dict(
            email='nonexistent@example.com',
            password='password'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Credentials don't match", response.data)

if __name__ == '__main__':
    unittest.main()
