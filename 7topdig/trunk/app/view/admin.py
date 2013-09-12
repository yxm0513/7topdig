# -*- coding: utf-8 -*- 
from flask import Blueprint, request, flash, url_for, redirect, \
     render_template, abort, session
from flaskext.login import current_user
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.mail import Message
from app.lib.permissions import admin
from app.forms import UserForm, MailAllForm
from feedparser import parse

from app import db, mail
from app.models import User, Post, Page, Tag
import setting
from data import createPost

"""
    定义admin模块，在app.__init__.py中加载, 本页面中只能是admin才能登录
"""
mod = Blueprint('admin', __name__)
################################################################################
#
# Functions and classes
#
################################################################################


################################################################################
#
# Routine to Admin view
#
################################################################################
"""
    管理首页
"""
@mod.route('/', methods = ['GET', 'POST'])
@mod.route('/index', methods = ['GET', 'POST'])
@admin.require(403)
def index():
    return render_template('admin/index.html')


"""
       用户的管理 
"""
@mod.route('/users', methods = ['GET', 'POST'])
@admin.require(403)
def users():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        try:
            user.save()
            flash(u"添加用户： %s 成功" % user.username, 'successfully')
        except:
            flash(u"添加用户： %s 失败" % user.username, 'error')
    
    users = User.query.all()
    return render_template('admin/users.html', users = users, form = form)

"""
       删除用户 
"""
@mod.route('/deluser', methods = ['GET', 'POST'])
@admin.require(403)
def deluser():
    username = request.args.get('username')
    user = User.query.filter_by(username = username).first()
    if not user:
        flash(u'用户不存在')
    else:
        try:
            user.delete()
            flash(u"删除用户： %s 成功" % user.username, 'successfully')
        except:
            flash(u"删除用户:%s 失败" % user.username, 'error')
    return redirect(url_for('admin.users'))

"""
        Page的管理 
"""
@mod.route('/pages', methods = ['GET', 'POST'])
@admin.require(403)
def pages():
    pages = Page.query.all()
    return render_template('admin/pages.html', pages = pages)


@mod.route("/delpage/<name>", methods = ['GET','POST'])
def delpage(name=None):
    page = Page.query.filter_by(name=name).first()
    if page:
        page.delete()
        flash(u"你删除了页面 %s" % page.name)
    else:
        flash(u"页面不存在")
    return redirect(url_for('admin.pages'))


"""
        Page的管理 
"""
@mod.route('/tags', methods = ['GET', 'POST'])
@admin.require(403)
def tags():
    tags = Tag.query.all()
    return render_template('admin/tags.html', tags = tags)


@mod.route("/deltag/<slug>", methods = ['GET','POST'])
@admin.require(403)
def deltag(slug=None):
    tag = Tag.query.filter_by(slug=name).first()
    if tag:
        tag.delete()
        flash(u"你删除了标签 %s" % tag.slug)
    else:
        flash(u"标签不存在")
    return redirect(url_for('admin.tags'))


"""
    Post的管理 
"""
@mod.route('/posts', methods = ['GET', 'POST'])
@admin.require(403)
def posts():
    posts = Post.query.all()
    if request.method == "POST":
        id = request.values.get('douban_id')
        book = parse(setting.DOUBAN_API_PATH + '/' + id)
        for e in book['entries']:
            if hasattr(e, 'summary'):
                post = createPost(current_user, e.title, e.summary)
            else:
                post = createPost(current_user, e.title, '')
            flash(u"添加Post： %s 成功" % e.title, 'successfully')
            return redirect(url_for('admin.posts'))
    return render_template('admin/posts.html', posts = posts)

"""
       删除Post 
"""
@mod.route('/delpost', methods = ['GET', 'POST'])
@admin.require(403)
def delpost():
    id = request.args.get('id')
    post = Post.query.filter_by(id = id).first()
    if not post:
        flash(u'Post不存在')
    else:
        try:
            post.delete()
            flash(u"删除Post： %s 成功" % name, 'successfully')
        except:
            flash(u"删除Post:%s 失败" % name, 'error')
    return redirect(url_for('admin.posts'))


"""
       给所有注册用户发邮件 
"""
@mod.route('/mailall', methods = ['GET', 'POST'])
@admin.require(403)
def mailall():
    """Sends an email to all users"""
    form = MailAllForm()
    
    if form.validate_on_submit():
        subject = request.values["subject"]
        message = request.values["message"]
        from_address = setting.ADMIN_MAIL
        with mail.connect() as conn:
            if setting.MAIL_ENABLE:
                for user in User.query:
                    message = Message(subject=subject,
                                      body=message,
                                      sender=from_address,
                                      recipients=[user.email])
                    conn.send(message)
                flash(u"邮件已发出", "successfully")
            else:
                flash(u"邮件服务器未开启，请联系管理员", "error")
                
    return render_template("admin/mailall.html", form = form)

