# -*- coding: utf-8 -*- 
from urlparse import urljoin
from flask import Blueprint, request, url_for, render_template, request
from werkzeug.contrib.atom import AtomFeed
from feedparser import parse
from datetime import datetime
from app.models import User, Post, Tag

"""
    定义feeds模块，在app.__init__.py中加载
"""
mod = Blueprint('feeds', __name__)

################################################################################
#
# Functions/Classes for feeds view
#
################################################################################
class PostFeed(AtomFeed):
    def add_post(self, post):
        if not post.title:
            post.title = "None"
        self.add(post.title,
                 unicode(post.markdown),
                 content_type="html",
                 author=post.author.username,
                 url=post.permalink,
                 updated=datetime.utcnow(),
                 published=post.date_created)

################################################################################
#
# Routine to Feeds view
#
################################################################################
"""
    index feeds
"""
@mod.route("/")
@mod.route("/index")
#@cached()
def index():
    feed = PostFeed("topdig - hot",
                    feed_url=request.url,
                    url=request.url_root)

    posts = Post.query.hottest().public().limit(15)
    for post in posts:
        feed.add_post(post)
    return feed.get_response()

"""
    latest feeds
"""
@mod.route("/latest/")
#@cached()
def latest():
    feed = PostFeed("topdig - new",
                    feed_url=request.url,
                    url=request.url_root)
    posts = Post.query.public().limit(15)
    for post in posts:
        feed.add_post(post)
    return feed.get_response()

"""
    deadpool feeds
"""
@mod.route("/deadpool/")
#@cached()
def deadpool():
    feed = PostFeed("topdig - deadpool",
                    feed_url=request.url,
                    url=request.url_root)
    posts = Post.query.deadpooled().public().limit(15)
    for post in posts:
        feed.add_post(post)
    return feed.get_response()

"""
    tag feeds
"""
@mod.route("/tag/<slug>/")
#@cached()
def tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    feed = PostFeed("topdig - %s"  % tag,
                    feed_url=request.url,
                    url=request.url_root)
    posts = tag.posts.public().limit(15)
    for post in posts:
        feed.add_post(post)
    return feed.get_response()

"""
    user feeds
"""
@mod.route("/user/<username>/")
#@cached()
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    feed = PostFeed("topdig - %s" % user.username,
                    feed_url=request.url,
                    url=request.url_root)
    posts = Post.query.filter_by(author_id=user.id).public().limit(15)
    for post in posts:
        feed.add_post(post)
    return feed.get_response()
