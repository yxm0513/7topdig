# -*- coding: utf-8 -*-
from datetime import datetime
from werkzeug import cached_property
from flask import Markup
from flaskext.sqlalchemy import BaseQuery
from flaskext.principal import Permission, UserNeed, Denial

from app.lib.util import DenormalizedText, dbFunctions, tomarkdown
from app import db, signals, comment_added, comment_deleted
from app.lib.permissions import auth, moderator, admin, Permissions
from app.models import Post, User


#######################################################################
#
#  Model for Comments
#
#######################################################################
class CommentQuery(BaseQuery):
    def restricted(self, user):
        if user and user.is_moderator:
            return self
       
        q = self.join(Post)
        criteria = [Post.access==Post.PUBLIC]

        if user:
            criteria.append(Post.author_id==user.id)
            if user.friends:
                criteria.append(db.and_(Post.access==Post.FRIENDS,
                                        Post.author_id.in_(user.friends)))
        return q.filter(reduce(db.or_, criteria))

   
class Comment(db.Model, dbFunctions):
    __tablename__ = "comments"
    PER_PAGE = 20
    query_class = CommentQuery

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    post_id = db.Column(db.Integer, 
                        db.ForeignKey(Post.id, ondelete='CASCADE'), 
                        nullable=False)
    parent_id = db.Column(db.Integer, 
                          db.ForeignKey("comments.id", ondelete='CASCADE'))
    comment = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, default=1)
    votes = db.Column(DenormalizedText)
    author = db.relation(User, innerjoin=True, lazy="joined")
    post = db.relation(Post, innerjoin=True, lazy="joined")
    parent = db.relation('Comment', remote_side=[id])

    __mapper_args__ = {'order_by' : id.asc()}
    
    class Permissions(Permissions):
        @cached_property
        def default(self):
            return Permission(UserNeed(self.author.username)) & moderator

        @cached_property
        def edit(self):
            return Permission(UserNeed(self.author.username)) & admin

        @cached_property
        def delete(self):
            return Permission(UserNeed(self.author.username)) & admin

        @cached_property
        def vote(self):

            needs = [UserNeed(User.query.get(user_id).username) for user_id in self.votes]
            needs.append(UserNeed(self.author.username))

            return auth & Denial(*needs)

   
    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.votes = self.votes or set()

    @cached_property
    def permissions(self):
        return self.Permissions(self)

    def vote(self, user):
        self.votes.add(user.id)

    def _url(self, _external=False):
        return '%s#comment-%d' % (self.post._url(_external), self.id)

    @cached_property
    def url(self):
        return self._url()

    @cached_property
    def permalink(self):
        return self._url(True)

    @cached_property
    def dateshow(self):
        return self.date_created.strftime("%c")

# ------------- SIGNALS ----------------#

def update_num_comments(sender):
    sender.num_comments = \
        Comment.query.filter(Comment.post_id==sender.id).count()
    
    db.session.commit()


#signals.comment_added.connect(update_num_comments)
#signals.comment_deleted.connect(update_num_comments)

