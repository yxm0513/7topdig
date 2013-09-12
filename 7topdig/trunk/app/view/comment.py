#-*- coding: utf-8 -*-
from flask import Blueprint, redirect, flash, g, jsonify, \
    current_app, render_template
from flaskext.login import current_user

from app.lib.permissions import auth
from app.models import Comment
from app.forms import CommentForm, CommentAbuseForm
import setting

"""
    定义comment模块，在app.__init__.py中加载
"""
mod = Blueprint('comment', __name__)
################################################################################
#
# Functions for Comment view
#
################################################################################
def _vote(comment_id, score):
    """
        vote一个评论
    """
    comment = Comment.query.get_or_404(comment_id)
    #comment.permissions.vote.test(403)
    
    comment.score += score
    comment.author.karma += score

    if comment.author.karma < 0:
        comment.author.karma = 0

    comment.vote(current_user)
    comment.save()

    return jsonify(success=True,
                   comment_id=comment_id,
                   score=comment.score)

################################################################################
#
# Routine to Comment View
#
################################################################################
"""
        更新评论：
        1. 查询到评论
        2. 更新之
"""
@mod.route("/<int:comment_id>/edit/", methods=['GET', 'POST'])
@auth.require(401)
def edit(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    #comment.permissions.edit.test(403)
    form = CommentForm(obj=comment)
    if form.validate_on_submit():
        form.populate_obj(comment)
        comment.save()
        flash(u"你的评论已更新", "successfully")
        return redirect(comment.url)
    return render_template("comment/edit.html",
                           comment=comment,
                           form=form)

"""
        删除评论：
        1. 查询到评论
        2. 删除之
"""
@mod.route("/<int:comment_id>/delete/", methods=("POST",))
@auth.require(401)
def delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.post.num_comments -= 1
    #comment.permissions.delete.test(403)
    comment.delete()
    #signals.comment_deleted.send(comment.post)

    return jsonify(success=True, reload=True,
                   comment_id=comment_id, 
                   redirect_url=comment.url)

"""
        举报无用评论：
        1. 查询到评论
        2. 发送邮件给审查员
"""
@mod.route("/<int:comment_id>/abuse/", methods=("GET", "POST",))
@auth.require(401)
def report_abuse(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    form = CommentAbuseForm()
    if form.validate_on_submit():
        admins = current_app.config['ADMINS']
        if admins and setting.MAIL_ENABLE:
            body = render_template("emails/reportabuse.html",
                               comment=comment,
                               complaint=form.complaint.data)
            
            message = Message(subject=u"内容举报",
                              body=body,
                              sender=current_user.email,
                              recipients=admins)

            mail.send(message)
            flash(u"你的意见已经发给了管理员", "successfully")
        else:
            flash(u"邮件服务器未开启，请联系管理员", "error")
        return redirect(comment.url)
    return render_template("comment/reportabuse.html",
                           comment=comment,
                           form=form)

"""
        顶评论：
"""
@mod.route("/<int:comment_id>/upvote/", methods=("POST",))
@auth.require(401)
def upvote(comment_id):
    return _vote(comment_id, 1)

"""
        踩评论：
"""
@mod.route("/<int:comment_id>/downvote/", methods=("POST",))
@auth.require(401)
def downvote(comment_id):
    return _vote(comment_id, -1)
