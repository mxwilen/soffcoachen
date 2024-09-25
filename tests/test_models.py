import unittest
from app import app, db, bcrypt
from app.models import User, Post, Team, Comment, PostLike, CommentLike
from dummy_data import generate_dummy, generate_teams
from sqlalchemy.exc import IntegrityError

pw = bcrypt.generate_password_hash('pw').decode('utf-8')

class ModelsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://localhost/maxwilen'
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            print("\n--- TESTING MODELS ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()
            generate_dummy(db)

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            print("\n--- DONE TESTING MODELS ---")
            generate_teams(db) # includes db.drop_all() and db.create_all()

    def test_user_model(self):
        with self.app.app_context():
            try:
                user1 = User(username='testuser', 
                             email='test@example.com', 
                             password=pw)
                db.session.add(user1)
                db.session.commit()
                # print("Testing User model: Successfully added user")
            except Exception as e:
                db.session.rollback()
                print("Testing User model: Error occurd: " + str(e))
        
            retrieved_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.id, user1.id)
            self.assertEqual(retrieved_user.email, 'test@example.com')

            with self.assertRaises(IntegrityError):
                # Attempt to create a second user with the same username
                user2 = User(username="testuser", 
                            email="test2@example.com", 
                            password=pw)
                db.session.add(user2)
                db.session.commit()

            db.session.rollback()


    def test_post_model(self):
        with self.app.app_context():
            try:
                user1 = User(username='testpost', 
                                email='test_post@example.com', 
                                password=pw)
                db.session.add(user1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                self.fail(f"Testing Post model: Error occurred adding user: {str(e)}")

            try:
                post1 = Post(title='Test Post', 
                                content='This is a test post', 
                                author=user1, 
                                team_name="AIK")
                db.session.add(post1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                self.fail(f"Testing Post model: Error occurred adding post: {str(e)}")

            # Retrieve the user and post to verify they were added correctly
            retrieved_user = User.query.get(user1.id)
            retrieved_post = Post.query.get(post1.id)
            self.assertIsNotNone(retrieved_user, "User should exist in the database")
            self.assertIsNotNone(retrieved_post, "Post should exist in the database")
            self.assertEqual(retrieved_post.content, 'This is a test post')
            self.assertEqual(retrieved_post.user_id, user1.id)
            
            # Attempt to create a second user with the same username or email
            with self.assertRaises(IntegrityError):
                duplicate_user = User(username='testpost', 
                                    email='test_post@example.com', 
                                    password=pw)
                db.session.add(duplicate_user)
                db.session.commit()

            # Ensure session is clean after testing
            db.session.rollback()

    
    def test_team_model(self):
        with self.app.app_context():
            retrieved_team = Team.query.filter_by(name='AIK').first()
            self.assertIsNotNone(retrieved_team)
            self.assertEqual(retrieved_team.city, 'Stockholm')
            self.assertEqual(retrieved_team.abr, 'aik')

            # Attempt to create a duplication of the team
            try:
                duplicate_team = Team(name='AIK', abr='aik', city='Stockholm')
                db.session.add(duplicate_team)
                db.session.commit()
                self.fail('IntegrityError not raised')  # Fail if no error
            except IntegrityError:
                print("SUCESS. Duplicate Team not added. db is rolled back.")
                db.session.rollback()  # Rollback the session after IntegrityError
            except Exception as e:
                self.fail(f'Unexpected exception raised: {e}')
    
    def test_comment_model(self):
        with self.app.app_context():
            try:
                user1 = User(username='testcomment', 
                             email='test_comment@example.com', 
                             password=pw)
                db.session.add(user1)
                db.session.commit()
                # print("Testing Comment model: Successfully added user")
            except Exception as e:
                db.session.rollback()
                print("Testing Comment model: Error occurd adding user: " + str(e))

            try:
                post1 = Post(title='Test Post', 
                             content='This is a test post', 
                             author=user1, 
                             team_name="AIK")
                db.session.add(post1)
                db.session.commit()
                # print("Testing Comment model: Successfully added post")
            except Exception as e:
                db.session.rollback()
                print("Testing Comment model: Error occurd adding post: " + str(e))

            
            try:
                comment1 = Comment(content='This is a test comment', 
                                   author=user1, 
                                   post=post1)
                db.session.add(comment1)
                db.session.commit()
                # print("Testing Comment model: Successfully added comment")
            except Exception as e:
                db.session.rollback()
                print("Testing Comment model: Error occurd adding post: " + str(e))

            
            try:
                child_comment = Comment(content='This is a test comment', 
                                        author=user1, 
                                        post=post1, 
                                        parent=comment1)
                db.session.add(child_comment)
                db.session.commit()
                # print("Testing Comment model: Successfully added child comment")
            except Exception as e:
                db.session.rollback()
                print("Testing Comment model: Error occurd adding child comment: " + str(e))


            retrieved_comment = Comment.query.filter_by(id=comment1.id).first()
            retrieved_child_comment = Comment.query.filter_by(id=child_comment.id).first()
            self.assertIsNotNone(retrieved_comment)
            self.assertIsNotNone(retrieved_child_comment)
            self.assertEqual(retrieved_comment.user_id, user1.id)
            self.assertEqual(retrieved_comment.post_id, post1.id)

            self.assertEqual(retrieved_child_comment.user_id, user1.id)
            self.assertEqual(retrieved_child_comment.post_id, post1.id)
            self.assertEqual(retrieved_child_comment.parent_id, comment1.id)

            # Ensure session is clean after testing
            db.session.rollback()

    
    def test_post_like_model(self):
        with self.app.app_context():
            try:
                user1 = User(username='testlikemodel', 
                             email='test_like_model@example.com', 
                             password=pw)
                db.session.add(user1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Testing PostLike model: Error occurd adding user: " + str(e))

            try:
                post1 = Post(title='Test Post', 
                             content='This is a test post', 
                             author=user1, 
                             team_name="AIK")
                db.session.add(post1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Testing PostLike model: Error occurd adding post: " + str(e))

            # Liking post1 with user1
            user1.like_post(post1)
            retrieved_like = PostLike.query.filter_by(user_id=user1.id, post_id=post1.id).first()
            self.assertIsNotNone(retrieved_like)
            self.assertTrue(user1.has_liked_post(post1))
            self.assertIsNone(user1.like_post(post1))

            # Un-liking post1 with user1
            user1.unlike_post(post1)
            retrieved_like = PostLike.query.filter_by(user_id=user1.id, post_id=post1.id).first()
            self.assertIsNone(retrieved_like)
            self.assertFalse(user1.has_liked_post(post1))

            # Ensure session is clean after testing
            db.session.rollback()

    def test_comment_like_model(self):
        with self.app.app_context():
            try:
                user1 = User(username='testcommentlike', 
                             email='test_comment_like@example.com', 
                             password=pw)
                db.session.add(user1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Testing CommentLike model: Error occurd adding user: " + str(e))

            try:
                post1 = Post(title='Test Post', 
                             content='This is a test post', 
                             author=user1, 
                             team_name="AIK")
                db.session.add(post1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Testing CommentLike model: Error occurd adding post: " + str(e))

            try:
                comment1 = Comment(content='This is a test comment', 
                                   author=user1, 
                                   post=post1)
                db.session.add(comment1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Testing CommentLike model: Error occurd adding post: " + str(e))

            # Liking comment1 with user1
            user1.like_comment(comment1)
            retrieved_like = CommentLike.query.filter_by(user_id=user1.id, comment_id=comment1.id).first()
            self.assertIsNotNone(retrieved_like)
            self.assertTrue(user1.has_liked_comment(comment1))
            self.assertIsNone(user1.like_comment(comment1))

            # Un-liking post1 with user1
            user1.unlike_comment(comment1)
            retrieved_like = CommentLike.query.filter_by(user_id=user1.id, comment_id=comment1.id).first()
            self.assertIsNone(retrieved_like)
            self.assertFalse(user1.has_liked_post(comment1))

            # Ensure session is clean after testing
            db.session.rollback()

    def test_follow(self):
        with self.app.app_context():
            try:
                user1 = User(username='testfollow1', 
                             email='test_follow1@example.com', 
                             password=pw)
                db.session.add(user1)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Testing CommentLike model: Error occurd adding user: " + str(e))

            try:
                user2 = User(username='testfollow2', 
                             email='test_follow2@example.com', 
                             password=pw)
                db.session.add(user2)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Testing CommentLike model: Error occurd adding user: " + str(e))

            user1.follow(user2)
            self.assertTrue(user1.is_following(user2))
            self.assertTrue(user2.is_followed_by(user1))
            self.assertFalse(user2.is_following(user1))

            with self.assertRaises(ValueError):
                user1.follow(user1)

            user1.unfollow(user2)
            self.assertFalse(user1.is_following(user2))
            self.assertFalse(user2.is_followed_by(user1))
            self.assertFalse(user2.is_following(user1))

            # Ensure session is clean after testing
            db.session.rollback()


if __name__ == '__main__':
    unittest.main()
