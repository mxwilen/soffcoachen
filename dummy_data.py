from app.models import User, Post, Team, Comment
from app import bcrypt

def generate_teams(db):
    db.drop_all()
    db.create_all()

    # Creation of team-data
    none = Team(name='-', abr='none')
    aik = Team(name='AIK', abr='aik', city='Stockholm')
    bkh = Team(name='BK Häcken', abr='bkh', city='Hissingen')
    dif = Team(name='Djurgårdens IF', abr='dif', city='Stockholm')
    gais = Team(name='Gais', abr='gais', city='Göteborg')
    hbk = Team(name='Halmstad BK', abr='hbk', city='Halmstad')
    hif = Team(name='Hammarby IF', abr='hif', city='Stockholm')
    ifbp = Team(name='IF Brommapojkarna', abr='ifbp', city='Stockholm')
    ife = Team(name='IF Elfsborg', abr='ife', city='Borås')
    ifkg = Team(name='IFK Göteborg', abr='ifkg', city='Göteborg')
    ifkn = Team(name='IFK Norrköping', abr='ifkn', city='Norrköping')
    ifkv = Team(name='IFK Värnamo', abr='ifkv', city='Värnamo')
    iks = Team(name='IK Sirius', abr='iks', city='Uppsala')
    kff = Team(name='Kalmar FF', abr='kff', city='Kalmar')
    mff = Team(name='Malmö FF', abr='mff', city='Malmö')
    maif = Team(name='Mjälby AIF', abr='maif', city='Sölvesborg')
    vsk = Team(name='Västerås SK', abr='vsk', city='Västerås')

    db.session.add_all([none, aik, bkh, dif, gais, hbk, hif, ifbp, ife, ifkg, ifkn, ifkv, iks, kff, mff, maif, vsk])
    db.session.commit()

def generate_dummy(db):
    pw = bcrypt.generate_password_hash('pw').decode('utf-8')
    # Create dummy data for users
    user1 = User(username='user1', email='user1@test.com', password=pw)
    user2 = User(username='user2', email='user2@test.com', password=pw)
    user3 = User(username='user3', email='user3@test.com', password=pw)

    # Create dummy data for posts
    post1 = Post(title='First Post', content='Content of first post.', author=user1)
    post2 = Post(title='Second Post', content='Content of second post.', author=user2)
    post3 = Post(title='third Post', content='Content of third post.', author=user3)

    # Create dummy data for comments
    comment1 = Comment(content='Content of first comment.', author=user1, post=post2)
    comment2 = Comment(content='Content of second comment.', author=user2, post=post3)
    comment3 = Comment(content='Content of third comment.', author=user3, post=post1)

    # Add users and posts to the session
    db.session.add_all([user1, user2, user3,
                        post1, post2, post3,
                        comment1, comment2, comment3])
    
    # Commit changes to the database
    db.session.commit()
    
    user1.follow(user2)
    user2.follow(user3)

    user1.like_post(post1)
    user1.like_post(post2)

    user1.like_comment(comment1)
    user1.like_comment(comment3)