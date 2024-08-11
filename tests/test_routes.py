import unittest
from app import app, db
from dummy_data import generate_dummy, generate_teams

class AppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://localhost/maxwilen'
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            print("--- TESTING ROUTES ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            print("--- DONE TESTING ROUTES ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()


    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
