import pytz
from flask import request, redirect, url_for, flash, Blueprint
from flask.json import jsonify
from datetime import datetime
from app.models import User, Post, Comment
# from app import app, db
from app import db
from flask import current_app as app
from flask_login import login_required
from .auth_routes import current_user

ajax_bp = Blueprint('ajax', __name__)

########################### AJAX ROUTES #################################
@ajax_bp.route('/post/<int:post_id>/update', methods=['POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash('try updating your own posts instead!', 'warning')
        return redirect(url_for('no_auth.home'))

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



@ajax_bp.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).all()
    
    if post.user_id != current_user.id and current_user.role != 'admin':
        flash('Try deleting your own posts instead!', 'warning')
        return redirect(url_for('no_auth.home'))
    
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
    return redirect(url_for('no_auth.home'))


@ajax_bp.route('/post/<int:post_id>/comment/<string:username>', methods=['GET', 'POST'])
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
                            post=post,
                            author=user,
                            parent=parent)
            else:
                comment = Comment(content=request.form.get('content'),
                                post=post,
                                author=user)
            
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


@ajax_bp.route('/like/post/<int:post_id>/<action>')
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

@ajax_bp.route('/like/comment/<int:comment_id>/<action>')
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
