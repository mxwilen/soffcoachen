import pytz
from flask import render_template, request, redirect, url_for, flash
from flask import Blueprint
from flask.json import jsonify
from datetime import datetime, timedelta

# from models import Restaurant, Review
from models import User, Post, Comment, Team, PostLike
from forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, CommentForm, UpdatePostForm, SearchPostsForm
from app import app, csrf, db, bcrypt, tags
from flask_login import login_user, current_user, logout_user, login_required

from routes.route_utils import get_image_path_no_name, save_picture, send_reset_email


home_bp = Blueprint('home', __name__)
team_bp = Blueprint('team', __name__)
about_bp = Blueprint('about', __name__)
register_bp = Blueprint('register', __name__)
login_bp = Blueprint('login', __name__)
logout_bp = Blueprint('logout', __name__)
account_bp = Blueprint('account', __name__)
post_bp = Blueprint('post', __name__)
update_post_bp = Blueprint('update_post', __name__)
delete_post_bp = Blueprint('delete_post', __name__)
comment_post_bp = Blueprint('comment_post', __name__)
comment_delete_bp = Blueprint('comment_delete', __name__)
like_post_action_bp = Blueprint('like_post_action', __name__)
like_comment_action_bp = Blueprint('like_comment_action', __name__)
follow_user_bp = Blueprint('follow_user', __name__)
user_posts_bp = Blueprint('user_posts', __name__)
reset_request_bp = Blueprint('reset_request', __name__)
reset_token_bp = Blueprint('reset_token', __name__)



"""
index_bp = Blueprint('index', __name__)
details_bp = Blueprint('details', __name__)
create_restaurant_bp = Blueprint('create_restaurant', __name__)
add_restaurant_bp = Blueprint('add_restaurant', __name__)
add_review_bp = Blueprint('add_review', __name__)
utility_bp = Blueprint('utility', __name__)
favicon_bp = Blueprint('favicon', __name__)


@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    restaurants = Restaurant.query.all()    
    return render_template('index.html', restaurants=restaurants)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    return details(id,'')

def details(id, message):
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant==id)
    image_path = get_account_url() + "/" +  STORAGE_CONTAINER_NAME
    return render_template('details.html', restaurant=restaurant, reviews=reviews, message=message, image_path=image_path)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
        if (name == "" or description == "" ):
            raise RequestException()
    except (KeyError, RequestException):
        # Redisplay the restaurant entry form.
        return render_template('create_restaurant.html', 
            message='Restaurant not added. Include at least a restaurant name and description.')
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        db.session.add(restaurant)
        db.session.commit()

        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')   
        if (user_name == "" or rating == None):
            raise RequestException()
    except (KeyError, RequestException):
        # Redisplay the review form.
        restaurant = Restaurant.query.where(Restaurant.id == id).first()
        reviews = Review.query.where(Review.restaurant==id)
        return details(id, 'Review not added. Include at least a name and rating for review.')
    else:
        if request.files['reviewImage']:
            image_data = request.files['reviewImage']

            # Get size.
            size = len(image_data.read())
            image_data.seek(0)

            print("Original image name = " + image_data.filename)
            print("File size = " + str(size))

            if (size > 2048000):
                return details(id, 'Image too big, try again.')

            # Get account_url based on environment
            print("account_url = " + get_account_url())

            # Create client
            azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
            blob_service_client = BlobServiceClient(
                account_url = get_account_url(),
                credential=azure_credential)

            # Get file name to use in database
            image_name = str(uuid.uuid4()) + ".png"
            
            # Create blob client
            blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=image_name)
            print("\nUploading to Azure Storage as blob:\n\t" + image_name)

            # Upload file
            blob_client.upload_blob(image_data)
        else:
            # No image for review
            image_name=None

        review = Review()
        review.restaurant = id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        review.image_name = image_name
        db.session.add(review)
        db.session.commit()
                
    return redirect(url_for('details', id=id))        
"""





########################### MITT EGET #################################
@app.errorhandler(400)
def bad_request(e):
    # Handles CSRF errors aswell.
    return render_template('400.html'), 400

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500



@app.route('/', methods=['GET', 'POST'])
def home():
    query = Post.query
    
    # For the "New post"-modal
    post_form = PostForm()
    if post_form.validate_on_submit():
        try:
            post = Post(title=post_form.title.data, 
                        content=post_form.content.data, 
                        user_id=current_user.id,
                        team=Team.query.filter_by(name=post_form.team.data).first(),
                        tag=post_form.tag.data,
                        locked=post_form.locked.data)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been submitted!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # Search field functionality
    search_form = SearchPostsForm()
    if search_form.validate_on_submit():
        check = search_form.check.data
        team = Team.query.filter_by(name=search_form.team.data).first()
        tag = search_form.tag.data

        if team and not team.name == '-':
        # if team and not team == '-':  # Use this to not list all teams when team is '-'
            print("t: ", team)
            query = query.filter_by(team=team)

        if tag:
            print("tag: ", tag)
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
        Post.date_posted < today_end
    ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(5).all()

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



@app.route('/team/<string:team>', methods=['GET', 'POST'])
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
                        user_id=current_user.id,
                        team=Team.query.filter_by(name=form.team.data).first(),
                        tag=form.tag.data,
                        locked=form.locked.data)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('team', team=team, tag=tag))
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
                           title=team,
                           post=paged_posts, 
                           post_form=form, 
                           team=team, 
                           tag=tag,
                           tags=tags,
                           most_liked_posts=most_liked_posts,
                           following_list=following_list,
                           no_of_posts=no_of_posts,
                           image_path=get_image_path_no_name(app))

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
            return redirect(url_for('home'))
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

@app.route('/login', methods=['GET', 'POST']) 
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
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

@app.route('/logout') 
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                # Save pictures flashes error if image-file is too big.
                current_user.image_file = save_picture(app, form.picture.data)
            
            if form.team.data:
                team_instance = Team.query.filter_by(name=form.team.data).first()
                
                if not team_instance:
                    flash('Something went wrong!', 'danger')
                
                if team_instance.name == '-':
                    current_user.team = None
                else:
                    current_user.team = team_instance

            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        if not current_user.team == None:
            form.team.data = current_user.team.name
        else: form.team.data = current_user.team

    # Query the 3 most liked posts from today
    today_start = datetime.now(pytz.timezone('Europe/Stockholm')).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    most_liked_posts = db.session.query(Post).outerjoin(PostLike).filter(
        Post.user_id == current_user.id
    ).group_by(Post.id).order_by(db.func.count(PostLike.id).desc()).limit(5).all()

    following_list = []
    if current_user.is_authenticated:
        following_list = current_user.followers

    return render_template('account.html', 
                           title='Account', 
                           form=form,
                           most_liked_posts=most_liked_posts,
                           following_list=following_list,
                           image_path=get_image_path_no_name(app))


@app.route('/post/<int:post_id>')
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



@app.route('/post/<int:post_id>/update', methods=['POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash('try updating your own posts instead!', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            post.title = request.form.get('title')
            post.content = request.form.get('content')
            post.date_edited = datetime.now(pytz.timezone('Europe/Stockholm'))
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return jsonify({"status": "success",
                            "date": post.date_edited})
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        flash('Something went wrong when updating the post.', 'danger')
        return jsonify({"status": "error", "message": "Post not found"}), 404



@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).all()
    if post.user_id != current_user.id:
        flash('Try deleting your own posts instead!', 'warning')
        return redirect(url_for('home'))
    
    try:
        for c in comments:
            db.session.delete(c)
        db.session.delete(post)
        db.session.commit()
        flash('The post and all its comments have been deleted!', 'success')
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>/comment/<string:username>', methods=['GET', 'POST'])
@login_required
def comment_post(post_id, username):

    if request.method == 'POST':
        try:
            post = Post.query.get_or_404(post_id)
            user = User.query.filter_by(username=username).first()
            
            if (post.is_locked() and (current_user.team_name != post.team_name)):
                flash('This comment is locked for supporters only.', 'warning')
                return jsonify({"status": "success"})

            if request.form.get('parent_comment_id'):
                p_id = request.form.get('parent_comment_id')
                parent = Comment.query.get_or_404(p_id)

                
                comment = Comment(content=request.form.get('content'),
                            post_id=post_id,
                            user_id=user.id,
                            parent=parent)
            else:
                comment = Comment(content=request.form.get('content'),
                                post_id=post_id,
                                user_id=user.id)
            
            db.session.add(comment)
            db.session.commit()
            flash('Your comment has been posted!', 'success')
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        flash('There was an error posting your comment.', 'danger')
    
    return jsonify({"status": "success"})


@app.route('/post/<int:post_id>/comment/delete/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def comment_delete(post_id, comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        if comment.user_id != current_user.id:
            flash('Error: try deleting your own comments instead!', 'warning')
            return redirect(url_for('home'))
        
        if comment.post_id != post_id:
            flash('Error: tried to delete a comment to another post!', 'warning')
            return redirect(url_for('home'))
        
        db.session.delete(comment)
        db.session.commit()
        flash('Your comment has been deleted!', 'success')
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('post', post_id=post_id))


@app.route('/like/post/<int:post_id>/<action>')
@login_required
def like_post_action(post_id, action):
    try:
        post = Post.query.filter_by(id=post_id).first_or_404()
        if action == 'like':
            current_user.like_post(post)
            db.session.commit()

        if action == 'unlike':
            current_user.unlike_post(post)
            db.session.commit()
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return jsonify({'like_count': post.likes.count()}, 
                   {'has_liked': current_user.has_liked_post(post)})

@app.route('/like/comment/<int:comment_id>/<action>')
@login_required
def like_comment_action(comment_id, action):
    try:
        comment = Comment.query.filter_by(id=comment_id).first_or_404()
        if action == 'like':
            current_user.like_comment(comment)
            db.session.commit()
        if action == 'unlike':
            current_user.unlike_comment(comment)
            db.session.commit()
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return jsonify({'like_count': comment.likes.count()}, 
                   {'has_liked': current_user.has_liked_comment(comment)})


@app.route('/follow/<int:user_id>')
@login_required
def follow_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first_or_404()
        if current_user == user:
            flash('Error: Cannot follow yourself!', 'warning')
            return redirect(request.referrer)
        
        if current_user.is_following(user):
            current_user.unfollow(user)
        else:
            current_user.follow(user)
        db.session.commit()
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(request.referrer)


@app.route('/user/<string:username>')
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
    
        following_list = user.followers
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



@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('invalid token error', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_pw
            db.session.commit()
            flash(f'Your password has been updated. Try logging in!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('reset_token.html', title='Reset Password', form=form)


########################### SLUT PÅ MITT EGET #################################





















