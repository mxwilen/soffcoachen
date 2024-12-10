import pytz
import os
from flask import Response, render_template, request, redirect, url_for, flash, abort, Blueprint
from datetime import datetime, timedelta

from app.models import User, Post, Comment, Team, PostLike
from app.forms import UpdateAccountForm, RequestResetForm
from flask import current_app as app
from app import db
from flask_login import current_user, logout_user, login_required

from .utils import get_image_path_no_name, save_picture, send_reset_email

auth_bp = Blueprint('auth', __name__)

########################### ROUTES THAT NEED AUTH #################################
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('no_auth.home'))


@auth_bp.route('/view-logs', methods=['GET'])
@login_required
def view_logs():
    """
    Route for viewing logs of form-input attempts containing typical injection characters
    """
    if current_user.role != 'admin':    # Restrict access to admins only
        abort(403)

    log_file = 'suspicious_activity.log'
    if not os.path.exists(log_file):
        return "Log file not found.", 404

    def generate():
        with open(log_file, 'r') as f:
            for line in f:
                yield line

    return Response(generate(), mimetype='text/plain')


@auth_bp.route('/account', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.account'))
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


@auth_bp.route('/post/<int:post_id>/comment/delete/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def comment_delete(post_id, comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        if current_user.role == 'admin':
            # ONLY FOR ADMIN. This stays segregated for sec. purposes.
            db.session.delete(comment)
            db.session.commit()
            flash(f'Comment has been deleted by admin: {current_user.username}', 'success')
            return redirect(url_for('no_auth.post', post_id=post_id))

        if comment.user_id != current_user.id:
            flash('Error: try deleting your own comments instead!', 'warning')
            return redirect(url_for('no_auth.home'))
        
        if comment.post_id != post_id:
            flash('Error: tried to delete a comment to another post!', 'warning')
            return redirect(url_for('no_auth.home'))
        
        db.session.delete(comment)
        db.session.commit()
        flash('Your comment has been deleted!', 'success')
    except Exception as e:
        # Rollback the transaction if there's an error
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('no_auth.post', post_id=post_id))


@auth_bp.route('/follow/<int:user_id>')
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

