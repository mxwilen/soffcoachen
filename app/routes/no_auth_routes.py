import pytz
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask.json import jsonify
from datetime import datetime, timedelta

from app.models import User, Post, Comment, Team, PostLike
from app.forms import RegistrationForm, LoginForm, PostForm, RequestResetForm, ResetPasswordForm, CommentForm, UpdatePostForm, SearchPostsForm
from app import db, bcrypt, limiter
from flask import current_app as app
from flask_login import login_user
from .auth_routes import current_user
from .utils import get_image_path_no_name, send_reset_email

from app.config_data import get_tags

# Safe image retrieval
from werkzeug.utils import safe_join

tags = get_tags()

no_auth_bp = Blueprint('no_auth', __name__)



########################### ROUTES THAT DON'T NEED AUTH #################################
"""
@app.route('/team-logo/')
def get_team_logo():
    # Use safe_join to ensure the path stays inside 'static/team-logos/'
    safe_path = safe_join('static/team-logos', 'dif.png')
    return safe_path

    # Check if the file exists
    if not os.path.isfile(safe_path):
      abort(404)  # Return 404 if the file doesn't exist
    return send_from_directory(safe_path)
"""
@no_auth_bp.route('/', methods=['GET', 'POST'])
def home():
    """
    Home/Start creen. Handles both authenticated and not authenticated users.
    """
    query = Post.query
    
    # For the "New post"-modal
    post_form = PostForm()
    if post_form.validate_on_submit():
        try:
            post = Post(title=post_form.title.data, 
                        content=post_form.content.data, 
                        author=current_user,
                        team=Team.query.filter_by(name=post_form.team.data).first(),
                        tag=post_form.tag.data,
                        locked=post_form.locked.data)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been submitted!', 'success')
            return redirect(url_for('no_auth.home'))
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            app.logger.error(f'An error occurred: {str(e)}')
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # Search field functionality
    search_form = SearchPostsForm()
    if search_form.validate_on_submit():
        check = search_form.check.data
        team = Team.query.filter_by(name=search_form.team.data).first()
        tag = search_form.tag.data

        if team and not team.name == '-':
        # if team and not team == '-':  # Use this to not list all teams when team is '-'
            query = query.filter_by(team=team)

        if tag:
            query = query.filter_by(tag=tag)

        if check:
            user_ids = [user.id for user in current_user.followers]
            query = query.filter(Post.user_id.in_(user_ids))
    
    # Paging of the posts on the frontpage
    ordered_posts = query.order_by(Post.date_posted.desc())
    no_of_posts = ordered_posts.count()
    page = request.args.get('page', 1, type=int)
    paged_posts = ordered_posts.paginate(page=page, per_page=20)

    # The list of teams used to print the logos on the frontpage.
    teams = [(team) for team in Team.query.all() if team.logo]


    # Query the 3 most liked posts from today
    today_start = datetime.now(pytz.timezone('Europe/Stockholm')).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    most_liked_posts = db.session.query(Post).outerjoin(PostLike).filter(
        Post.date_posted >= today_start,
        Post.date_posted < today_end,
        PostLike.id.isnot(None)
    ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(10).all()

    following_list = []
    if current_user.is_authenticated:
        following_list = current_user.followers

    return render_template('home.html',
                           post=paged_posts, 
                           post_form=post_form,
                           search_form=search_form,
                           teams=teams,
                           tags=tags,
                           most_liked_posts=most_liked_posts,
                           following_list=following_list,
                           no_of_posts=no_of_posts,
                           image_path=get_image_path_no_name(app=app))


@no_auth_bp.route('/team/<string:team>', methods=['GET', 'POST'])
def team(team, tag=None):
    tag = request.args.get('tag')
    page = request.args.get('page', 1, type=int)

    if tag != None:
        ordered_posts = Post.query.filter((Post.team_name.like(team) & Post.tag.like(tag))).order_by(Post.date_posted.desc())
    else:
        ordered_posts = Post.query.filter(Post.team_name.like(team)).order_by(Post.date_posted.desc())        
    
    no_of_posts = ordered_posts.count()
    paged_posts = ordered_posts.paginate(page=page, per_page=20)

    # For the "New post"-modal
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(title=form.title.data, 
                        content=form.content.data, 
                        author=current_user,
                        team=Team.query.filter_by(name=form.team.data).first(),
                        tag=form.tag.data,
                        locked=form.locked.data)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('no_auth.team', team=team, tag=tag))
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    team = Team.query.filter_by(name=team).first()


    # Query the 3 most liked posts from today
    today_start = datetime.now(pytz.timezone('Europe/Stockholm')).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    most_liked_posts = db.session.query(Post).outerjoin(PostLike).filter(
        Post.date_posted >= today_start,
        Post.date_posted < today_end,
        Post.team_name == team.name
    ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(5).all()

    following_list = []
    if current_user.is_authenticated:
        following_list = current_user.followers

    return render_template('team.html',
                           title=team.name,
                           post=paged_posts, 
                           post_form=form, 
                           team=team, 
                           tag=tag,
                           tags=tags,
                           most_liked_posts=most_liked_posts,
                           following_list=following_list,
                           no_of_posts=no_of_posts,
                           image_path=get_image_path_no_name(app))


@no_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register new user
    """
    if current_user.is_authenticated:
        return redirect(url_for('no_auth.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, 
                        email=form.email.data, 
                        team=Team.query.filter_by(name=form.team.data).first(),
                        password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Account has been created, and you have been logged in. Welcome!', 'success')
            return redirect(url_for('no_auth.home'))
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # Query the 3 most liked posts from today
    today_start = datetime.now(pytz.timezone('Europe/Stockholm')).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    most_liked_posts = db.session.query(Post).outerjoin(PostLike).filter(
        Post.date_posted >= today_start,
        Post.date_posted < today_end,
    ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(5).all()

    return render_template('register.html', 
                           title='Register', 
                           form=form,
                           most_liked_posts=most_liked_posts)


@no_auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Allow 5 login attempts per minute
def login():
    form = LoginForm()
    #validate_on_submit verifies POST submission and executed the custom validation functions
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('no_auth.home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')

    # Query the 3 most liked posts from today
    today_start = datetime.now(pytz.timezone('Europe/Stockholm')).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    most_liked_posts = db.session.query(Post).outerjoin(PostLike).filter(
        Post.date_posted >= today_start,
        Post.date_posted < today_end,
    ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(5).all()

    return render_template('login.html', 
                           title='Login', 
                           form=form,
                           most_liked_posts=most_liked_posts)


@no_auth_bp.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).all()
    
    comment_form = CommentForm()
    update_form = UpdatePostForm()


    # Query the 3 most liked posts from today
    today_start = datetime.now(pytz.timezone('Europe/Stockholm')).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    most_liked_posts = db.session.query(Post).outerjoin(PostLike).filter(
        Post.date_posted >= today_start,
        Post.date_posted < today_end,
        Post.tag == post.tag
    ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(5).all()

    following_list = []
    if current_user.is_authenticated:
        following_list = current_user.followers
    
    has_comments = post.has_comments()

    return render_template('post.html', 
                           post=post, 
                           comments=comments,
                           comment_form=comment_form,
                           update_form=update_form,
                           most_liked_posts=most_liked_posts,
                           following_list=following_list,
                           has_comments=has_comments,
                           image_path=get_image_path_no_name(app))


@no_auth_bp.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)
    ordered_posts = posts.order_by(Post.date_posted.desc())
    paged_posts = ordered_posts.paginate(page=page, per_page=5)
        
    no_of_user_comments = user.comment_count()
    no_of_recieved_likes = user.recieved_likes_count()
    no_of_followers = len(user.followed)

    most_liked_posts = None
    following_list = []
    is_following = False

    if current_user.is_authenticated:
        most_liked_posts = db.session.query(Post).outerjoin(PostLike).filter(
            Post.user_id == user.id
        ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(5).all()
    
        following_list = current_user.followers
        is_following = current_user.is_following(user)
    
    return render_template('user_posts.html',
                           title=f"{username}'s posts",
                           post=paged_posts, 
                           user=user, 
                           no_of_user_comments=no_of_user_comments,
                           no_of_recieved_likes=no_of_recieved_likes,
                           no_of_followers=no_of_followers,
                           most_liked_posts=most_liked_posts,
                           following_list=following_list,
                           is_following=is_following,
                           image_path=get_image_path_no_name(app))    


@no_auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('no_auth.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to reset your password.', 'info')
        return redirect(url_for('no_auth.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@no_auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('no_auth.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('invalid token error', 'warning')
        return redirect(url_for('no_auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_pw
            db.session.commit()
            flash(f'Your password has been updated. Try logging in!', 'success')
            return redirect(url_for('no_auth.login'))
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('reset_token.html', title='Reset Password', form=form)
