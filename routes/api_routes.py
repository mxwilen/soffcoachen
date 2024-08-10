import pytz
from flask import render_template, request, redirect, url_for, flash
from flask import Blueprint
from flask.json import jsonify
from datetime import datetime, timedelta

# from models import Restaurant, Review
from models import User, Post, Comment, Team, PostLike
from forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, CommentForm, UpdatePostForm, SearchPostsForm
from app import app, db, bcrypt, tags
from flask_login import login_user, current_user, logout_user, login_required

from routes.route_utils import get_image_path_no_name, save_picture, send_reset_email


########################### API PAGES #################################
@app.route('/api/home')
def api_home():
    query = Post.query
    
    posts = [(post.to_dict()) for post in query.order_by(Post.date_posted.desc()).all()]

    # The list of teams used to print the logos on the frontpage.
    teams = [(team.to_dict()) for team in Team.query.all() if team.logo]

    following_list = []
    if current_user.is_authenticated:
        following_list = current_user.followers

    if current_user.is_authenticated:
        cur_usr = current_user.username
    else:
        cur_usr = "not_auth"
    
    return jsonify({'status': "success",
                    'teams': teams,
                    'posts': posts,
                    'current_user': cur_usr})

@app.route('/api/login', methods=['GET', 'POST']) 
def api_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            
            following_list = [(user.username) for user in user.followers]
            return jsonify({'status': "login_success",
                            'current_user': current_user.username,
                            'following_list': following_list})
        else:
            print("error during login")
            jsonify({"status": "error", "message": "Something went wrong"}), 404

    return render_template('api_templates/api_login.html',
                           title='Login', 
                           form=form)

@app.route('/api/register', methods=['GET', 'POST'])
def api_register():
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
            following_list = [(user.username) for user in user.followers]
            return jsonify({'status': "register_success",
                            'current_user': current_user.username,
                            'following_list': following_list})
        
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            print("error: ", str(e))
            jsonify({"status": str(e)})

    return render_template('api_templates/api_register.html', 
                           title='Register', 
                           form=form)

@app.route('/api/logout')
@login_required
def api_logout():
    logout_user()
    return jsonify({'status': "logout_success"})

@app.route('/api/new_post', methods=['GET', 'POST'])
@login_required
def api_new_post():
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
            return "new_post_success"
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            print("error: ", str(e))
            jsonify({"status": "error", "message": "Something went wrong"}), 404

    return render_template('api_templates/api_new_post_template.html',
                           post_form=post_form)

@app.route('/api/new_comment', methods=['GET', 'POST'])
@login_required
def api_new_comment():
    post_id = request.args.get('post_id')
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        try:
            post = Post.query.get_or_404(post_id)
            
            if (post.is_locked() and (current_user.team_name != post.team_name)):
                return jsonify({"status": "error. post is locked."})
            
            comment = Comment(content=comment_form.content.data,
                        post_id=post_id,
                        user_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            return "new_comment_success"
        
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            print("error: ", str(e))
            jsonify({"status": str(e)})

    return render_template('api_templates/api_new_comment_template.html',
                           comment_form=comment_form)

@app.route('/api/account', methods=['GET', 'POST'])
@login_required
def api_account():
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
            return jsonify({'status': "account_update_success",
                            'current_user': current_user.username})
        
        except Exception as e:
            # Rollback the transaction if there's an error
            db.session.rollback()
            print("error: ", str(e))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        if not current_user.team == None:
            form.team.data = current_user.team.name
        else: form.team.data = current_user.team

    following_list = []
    if current_user.is_authenticated:
        following_list = current_user.followers

    return render_template('api_templates/api_account.html', 
                           title='Account', 
                           form=form,
                           following_list=following_list,
                           image_path=get_image_path_no_name(app))

@app.route('/api/post')
def api_post():
    post_id = request.args.get('post_id')

    post = Post.query.get_or_404(post_id)

    comments = [(comment.to_dict()) for comment in Comment.query.filter_by(post_id=post.id).all()]
    
    has_comments = post.has_comments()

    return jsonify({'post': post.to_dict(),
                    'comments': comments,
                    'has_comments': has_comments})

@app.route('/api/like/post/')
# @login_required
def api_like_post_action():
    post_id = request.args.get('post_id')

    try:
        print("user: ", current_user.username)
        if not current_user.is_authenticated:
            print("not authenticated")
            return jsonify({'status': "error: user not logged in."})
        
        post = Post.query.filter_by(id=post_id).first_or_404()
        if current_user.has_liked_post(post):
            print("un-liking post: ", post.id)
            current_user.unlike_post(post)
            db.session.commit()

        else:
            print("liking post: ", post.id)
            current_user.like_post(post)
            db.session.commit()

        return jsonify({'status': "like_post_success",
                        'like_count': str(post.likes.count()), 
                        'has_liked': current_user.has_liked_post(post)})
    
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        print("error: ", str(e))
        return jsonify({'status': str(e)})

@app.route('/api/like/comment/')
# @login_required
def api_like_comment_action():
    comment_id = request.args.get('comment_id')
    
    try:
        comment = Comment.query.filter_by(id=comment_id).first_or_404()
        if current_user.has_liked_comment(comment):
            print("un-liking comment: ", comment.id)
            current_user.unlike_comment(comment)
            db.session.commit()
        else:
            print("liking comment: ", comment.id)
            current_user.like_comment(comment)
            db.session.commit()
        
        return jsonify({'status': "like_comment_success",
                        'like_count': str(comment.likes.count()),
                        'has_liked': current_user.has_liked_comment(comment)})

    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        print("error: ", str(e))
        return jsonify({'status': str(e)})
    

@app.route('/api/user')
def api_user_posts():
    username = request.args.get('username')

    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)
    ordered_posts = posts.order_by(Post.date_posted.desc())

    posts = [(post.to_dict()) for post in ordered_posts]
        
    no_of_user_comments = user.comment_count()
    no_of_recieved_likes = user.recieved_likes_count()
    no_of_followers = len(user.followed)

    return jsonify({'title': f"{username}'s posts",
                    'user_team': user.team_name,
                    'posts': posts,
                    'no_of_user_comments': str(no_of_user_comments),
                    'no_of_recieved_likes': str(no_of_recieved_likes),
                    'no_of_followers': str(no_of_followers)})

@app.route('/api/follow')
@login_required
def api_follow_user():
    username = request.args.get('username')
    try:
        user = User.query.filter_by(username=username).first_or_404()
        if current_user == user:
            return jsonify({'status': "Error: Cannot follow yourself!"})
        
        if current_user.is_following(user):
            print("un-following user", user.username)
            current_user.unfollow(user)
        else:
            print("following user", user.username)
            current_user.follow(user)
        db.session.commit()

        if current_user.is_authenticated:
            is_following = current_user.is_following(user)

        return jsonify({'status': "follow_user_success",
                        'is_following': is_following})
    
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        print("error: ", str(e))
        return jsonify({'status': str(e)})