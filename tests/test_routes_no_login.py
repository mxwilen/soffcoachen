import unittest
from app import app, db
from dummy_data import generate_dummy, generate_teams

"""
This file only tests unauthorized requests.
"""
class RoutesNoLogin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://localhost/maxwilen'
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            print("\n--- TESTING ROUTES (no login) ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            print("\n--- SUCCESS TESTING ROUTES (no login) ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()


    def test_home_page(self):
        response = self.client.get('/api/home')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/api/login')
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        response = self.client.get('/api/register')
        self.assertEqual(response.status_code, 200)

    def test_logout_page(self):
        # Logout without being logged in.
        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 302)

    def test_new_post_page(self):
        # New post without being logged in.
        response = self.client.get('/api/new_post')
        self.assertEqual(response.status_code, 302)

    def test_new_comment_page(self):
        # New comment without being logged in.
        response = self.client.get('/api/new_comment?post_id=1')
        self.assertEqual(response.status_code, 302)

    def test_account_page(self):
        # Account page without being logged in.
        response = self.client.get('/api/account')
        self.assertEqual(response.status_code, 302)

    def test_post_page(self):
        response = self.client.get('/api/post?post_id=1')
        self.assertEqual(response.status_code, 200)

    def test_like_post_page(self):
        # Like post without being logged in.
        response = self.client.get('/api/like/post?post_id=1')
        self.assertEqual(response.status_code, 308)

    def test_like_comment_page(self):
        # Like comment without being logged in.
        response = self.client.get('/api/like/comment?comment_id=1')
        self.assertEqual(response.status_code, 308)

    def test_user_posts_page(self):
        response = self.client.get('/api/user?username=user1')
        self.assertEqual(response.status_code, 200)

    def test_follow_page(self):
        # Follow user without being logged in.
        response = self.client.get('/api/follow')
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()
