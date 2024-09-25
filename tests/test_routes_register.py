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

            cls.client.post('/api/register', data=dict(
                    username='test_register_again',
                    email='testregister_again@example.com',
                    team='AIK',
                    password='pw',
                    confirm_password='pw'
                ), follow_redirects=True)

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            print("\n--- SUCCESS TESTING REGISTER ROUTES ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

    def test_register_success(self):
        # POST request to register
        response = self.client.post('/api/register', data=dict(
            username='test_register',
            email='testregister@example.com',
            team='AIK',
            password='pw',
            confirm_password='pw'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"register_success", response.data)

    def test_register_failure(self):
        # POST request with bad email
        response = self.client.post('/api/register', data=dict(
            username='test_register',
            email='testregister.com',
            team='AIK',
            password='pw',
            confirm_password='pw'
        ), follow_redirects=True)

        # Bad email should not generate error page, but only provide the form again.
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"register_success", response.data)

    def test_login_no_user(self):
        # POST request with already existing user credentials
        response = self.client.post('/api/register', data=dict(
            username='test_register_again',
            email='testregister_again@example.com',
            team='AIK',
            password='pw',
            confirm_password='pw'
        ), follow_redirects=True)

        # Already assigned credentials should not generate error page, but only provide the form again.
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"register_success", response.data)

if __name__ == '__main__':
    unittest.main()
