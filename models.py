import pytz
import os
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer

from sqlalchemy import Column, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import validates
from flask_login import UserMixin

from app import db, login_manager, app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""
class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))
    def __str__(self):
        return self.name

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)
    image_name = Column(String(100))

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return self.restaurant.name + " (" + self.review_date.strftime("%x") +")"
"""



class User(db.Model, UserMixin):
    # __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Europe/Stockholm')))

    # team = db.Column(db.String(20), nullable=True)
    team_name = db.Column(db.String(50), db.ForeignKey('team.name'), nullable=True)
    team = db.relationship('Team', backref='members', lazy=True)
    
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    liked = db.relationship('PostLike', foreign_keys='PostLike.user_id', backref='author', lazy='dynamic')


    # Association table for the (follow user) many-to-many relationship.
    follows = Table('follows', db.metadata,
        Column('follower_id', Integer, ForeignKey('user.id'), primary_key=True),
        Column('followed_id', Integer, ForeignKey('user.id'), primary_key=True)
    )
    followers = db.relationship('User', 
                             secondary=follows, 
                             primaryjoin=(follows.c.followed_id == id), 
                             secondaryjoin=(follows.c.follower_id == id), 
                             backref='followed')

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    

    # PostLike actions
    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0
    

    # CommentLike actions
    def like_comment(self, comment):
        if not self.has_liked_comment(comment):
            like = CommentLike(user_id=self.id, comment_id=comment.id)
            db.session.add(like)

    def unlike_comment(self, comment):
        if self.has_liked_comment(comment):
            CommentLike.query.filter_by(
                user_id=self.id,
                comment_id=comment.id).delete()

    def has_liked_comment(self, comment):
        return CommentLike.query.filter(
            CommentLike.user_id == self.id,
            CommentLike.comment_id == comment.id).count() > 0
    

    # Count comments & likes
    def comment_count(self):
        return Comment.query.filter_by(user_id=self.id).count()
    
    def recieved_likes_count(self):
        return db.session.query(db.func.count(PostLike.id)).join(Post).filter(Post.user_id == self.id).scalar()
    

    # Follow actions
    def follow(self, user):
        if not self.is_following(user):
            self.followers.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followers.remove(user)
    
    def is_following(self, user):
        return user in self.followers
    
    def is_followed_by(self, user):
        return user in self.followed
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    # __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Europe/Stockholm')))
    date_edited = db.Column(db.DateTime, nullable=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    team_name = db.Column(db.String(50), db.ForeignKey('team.name'))
    team = db.relationship('Team', backref='post', lazy=True)
    
    tag = db.Column(db.String(50), nullable=True)

    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')

    locked = db.Column(db.Boolean, default=False)

    def has_comments(self):
        return self.comments.count() > 0

    def is_locked(self):
        return self.locked
    
    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'id': self.id,
            'date_posted': self.date_posted,
            'no_of_likes': str(self.likes.count()),
            'team': self.team_name,
            'tag': self.tag,
            'author': self.author.username,
            'user_id': self.user_id,
            'user_team': self.author.team_name
        }

    def __repr__(self):
        return f"Post('{self.title}', '{self.user_id}', '{self.date_posted}')"
    

class Team(db.Model):
    # __tablename__ = 'teams'
    name = db.Column(db.String(50), primary_key=True)
    abr = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    championships = db.Column(db.Integer, default=0)

    logo = db.Column(db.Text, nullable=True)

    def __init__(self, name, abr, city=None, championships=0):
        self.name = name
        self.abr = abr
        self.city = city
        self.championships = championships

        if not self.name == '-':
            self.logo = self.set_logo()

    def set_logo(self):
        return os.path.join(app.root_path, 'static', 'team-logos', self.abr + '.png')
    
    def to_dict(self):
        return {
            'name': self.name,
            'abr': self.abr
        }

    def __repr__(self):
        return f'<Team {self.name}>'



class Comment(db.Model):
    # __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_commented = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Europe/Stockholm')))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic')

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'date_commented': self.date_commented,
            'author': self.author.username,
            'author_team': self.author.team_name,
            'no_of_likes': str(self.likes.count())
        }

    def __repr__(self):
        return f"Comment('{self.id}', made by user: '{self.user_id}', on: '{self.date_commented}')"

class PostLike(db.Model):
    # __tablename__ = 'postlikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class CommentLike(db.Model):
    # __tablename__ = 'commentlikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))