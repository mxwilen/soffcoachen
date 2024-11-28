from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from . import tags, teams

import logging


def validate_no_injection_characters(form, field):
    """
    Ensures that the field does not contain characters commonly used in SQL injection.
    This is already checked by SQLAlchemy, but why not check it twice :)

    Logging is done if this func raises error. Check view-logs route to access them as 'admin'.
    """
    forbidden_characters = ["'", '"', "#", ";", "--", "\\", "/"]
    for char in forbidden_characters:
        if char in field.data:
            logging.warning(f"Suspicious input detected in field '{field.name}': {field.data}")
            raise ValidationError(f"The character '{char}' is not allowed.")


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), 
                                                   Length(min=2, max=100),
                                                   validate_no_injection_characters])
    email = StringField('Email', validators=[DataRequired(), 
                                             Email(),
                                             validate_no_injection_characters])
    team = SelectField('Favorite Team *', choices=teams, validators=[validate_no_injection_characters])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     validate_no_injection_characters])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), 
                                                                     EqualTo('password'),
                                                                     validate_no_injection_characters])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken')
        
    def validate_password(form, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must include at least one number.")
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must include at least one uppercase letter.")

        

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), 
                                             Email(), 
                                             validate_no_injection_characters])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     validate_no_injection_characters])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), 
                                                   Length(min=2, max=20),
                                                   validate_no_injection_characters])
    email = StringField('Email', validators=[DataRequired(), 
                                             Email(),
                                             validate_no_injection_characters])
    team = SelectField('Favorite Team *', choices=teams, validators=[validate_no_injection_characters])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png']),
                                                              validate_no_injection_characters])
    submit = SubmitField('Update profile')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('That email is already taken')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),
                                             validate_no_injection_characters])
    content = TextAreaField('Content', validators=[DataRequired(),
                                                   validate_no_injection_characters])
    team = SelectField('Team', choices=teams, validators=[validate_no_injection_characters])
    tag = SelectField('Tag', choices=tags, validators=[validate_no_injection_characters])
    locked = BooleanField('Commentable for supporters only?')
    submit = SubmitField('Submit post')

class UpdatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),
                                             validate_no_injection_characters])
    content = TextAreaField('Content', validators=[DataRequired(),
                                                   validate_no_injection_characters])
    submit = SubmitField('Submit post')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), 
                                             Email(),
                                             validate_no_injection_characters])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is None:
            raise ValidationError('If the email is registered, then it was successfully sent.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(),
                                                     validate_no_injection_characters])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), 
                                                                     EqualTo('password'),
                                                                     validate_no_injection_characters])
    submit = SubmitField('Reset Password')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(),
                                                   validate_no_injection_characters])
    submit = SubmitField('Submit comment')


class SearchPostsForm(FlaskForm):
    check = BooleanField('Only followed profiles?')
    team = SelectField('Team', choices=teams, validators=[validate_no_injection_characters])
    tag = SelectField('Tag', choices=tags, validators=[validate_no_injection_characters])
    submit = SubmitField('Search')

