# -*- coding: utf-8 -*-
from flask import Blueprint, abort, jsonify, request,  \
    url_for, redirect, flash, render_template, current_app, \
    make_response
from flaskext.login import current_user
from app.models import Post, Comment, User, save_action
from app.forms import CommentForm, PostForm
from app import db, mail, cache
from app.lib.permissions import auth
from flaskext.mail import Message
import setting
from datetime import datetime, timedelta
#from blinker import Namespace
#mysignals = Namespace()
#
#comment_added = mysignals.signal("comment-added")
#comment_deleted = mysignals.signal("comment-deleted")
#
#
#@comment_added.connect
#def comment_added(post):
#    post.num_comments += 1


"""
    定义post模块，在app.__init__.py中加载
"""
mod = Blueprint('post', __name__)

################################################################################
#
# Functions
#
################################################################################
def _vote(post_id, score):
    post = Post.query.get_or_404(post_id)

    cookie = request.cookies.get('vote-' + str(post.id))
    if cookie:
        return jsonify(success=False,
                       post_id=post_id,
                       error=u"同一条目，3分钟之内只能投票一次")
        
    save_action(u"投票  " + u'"' + post.title + u" " + str(score) +  u'"' )
    post.score += score
    post.author.karma += score

    if post.author.karma < 0:
        post.author.karma = 0

    post.vote(current_user)
    post.save()
    
    # make cookie to save user_action
    resp = jsonify(success=True,
                   reload=True,
                   post_id=post_id,
                   score=post.score)
    response = current_app.make_response(resp)
    expires = datetime.utcnow() + timedelta(minutes=3)
    response.set_cookie('vote-' + str(post.id),value=post.id, expires=expires)
    return response

################################################################################
#
# Routine to Post view
#
################################################################################
@mod.route("/<int:post_id>/")
@mod.route("/<int:post_id>/s/<slug>/")
#@cache.cached(unless=lambda: current_user is not None)
#@keep_login_url
def view(post_id, slug=None):
    post = Post.query.get_or_404(post_id)
    if not post.permissions.view:
        if not current_user:
            flash(u"你需要先登录", "error")
            return redirect(url_for("account.login", next=request.path))
        else:
            flash(u"你需要有权限", "error")
            abort(403)

    def edit_comment_form(comment):
        return CommentForm(obj=comment)

    return render_template("post/post.html", 
                           comment_form=CommentForm(),
                           edit_comment_form=edit_comment_form,
                           post=post)


@mod.route("/<int:post_id>/upvote/", methods=("POST","GET"))
@auth.require(403)
def upvote(post_id):
        return _vote(post_id, 1)


@mod.route("/<int:post_id>/downvote/", methods=("POST","GET"))
@auth.require(401)
def downvote(post_id):
    return _vote(post_id, -1)


@mod.route("/<int:post_id>/addcomment/", methods=['GET', 'POST'])
@mod.route("/<int:post_id>/<int:parent_id>/reply/", methods=['GET', 'POST'])
@auth.require(401)
def add_comment(post_id, parent_id=None):
    post = Post.query.get_or_404(post_id)
    post.permissions.view.test(403)
    parent = Comment.query.get_or_404(parent_id) if parent_id else None
    
    #user = User.query.first()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(post=post,
                          parent=parent,
                          author=current_user)
        form.populate_obj(comment)
        comment.save()
        post.num_comments += 1
        post.save()

        save_action(u"评论了条目 " + u'"' + post.title + u'"' )

        #comment_added.send()
        flash(u"谢谢你的评论", "successfully")
        author = parent.author if parent else post.author

        if author.email_alerts and author.id != current_user.id:
            if setting.MAIL_ENABLE:
                subject = u"有人回复了你的评论" if parent else \
                          u"有人给你的提交添加了评论"
                template = "emails/comment_replied.html" if parent else \
                           "emails/post_commented.html"
                body = render_template(template,
                                       author=author,
                                       post=post,
                                       parent=parent,
                                       comment=comment)
                mail.send_message(subject=subject,
                                  body=body,
                                  recipients=[post.author.email])
                flash(u"谢谢，你的邮件已发出", "successfully")
            else:
                flash(u"邮件服务器未开启，请联系管理员", "error")
        return redirect(comment.url)
    return render_template("post/add_comment.html",
                           parent=parent,
                           post=post,
                           form=form)

@mod.route("/<int:post_id>/edit/", methods=['GET', 'POST'])
@auth.require(401)
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    post.permissions.edit.test(403)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        post.save()
        flash(u"你的条目已更新", "successfully")
        return redirect(url_for("post.view", post_id=post_id))
    return render_template("post/edit_post.html", 
                           post=post, 
                           form=form)


@mod.route("/<int:post_id>/delete/", methods=("POST",))
@auth.require(401)
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    post.permissions.delete.test(403)
    post.delete()
    if current_user.id != post.author_id:
        if setting.MAIL_ENABLE: 
            body = render_template("emails/postdeleted.html",
                                   post=post)
            message = Message(subject=u"你提交的条目已删除",
                              body=body,
                              recipients=[post.author.email])
    
            mail.send(message)
            flash(u"条目已被删除", "successfully")
        else:
            flash(u"邮件服务器未开启，请联系管理员", "error")
    else:
        flash(u"你的条目成功删除", "successfully")
    return jsonify(success=True,
                   redirect_url=url_for('home.index'))

