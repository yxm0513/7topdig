# -*- coding: utf-8 -*-
from flask import url_for, Markup
from flaskext.sqlalchemy import SQLAlchemy, BaseQuery
from flaskext.principal import RoleNeed, UserNeed, Permission
from datetime import datetime
import random

from sqlalchemy import types
from sqlalchemy.orm import backref, relationship
from werkzeug.security import generate_password_hash, check_password_hash
#from forms import photos
from werkzeug import cached_property
from app.lib.permissions import Permissions, moderator, auth, admin
from app.lib.util import DenormalizedText, dbFunctions, slugify,\
    tomarkdown, domain
from app import db
from app.models import User
from flaskext.principal import Permission, UserNeed, Denial

from markdown import Markdown
YMK = Markdown(extensions=['fenced_code', 'tables'])


#######################################################################
#
#  Model for Message
#
#######################################################################
class MessageQuery(BaseQuery):
    def own_by(self, user=None):
        return self.filter(Message.owner == user)
    
    def send_by(self, user=None):
        return self.filter(Message.sender == user)

    def recive_by(self, user=None):
        return self.filter(Message.receiver == user)

    def latest_order(self):
        return self.order_by(Message.date_created.desc())
    
    def read(self, yes=False):
        if yes:
            return self.filter(Message.read == True)
        else:
            return self.filter(Message.read == False)

    def jsonify(self):
        for message in self.all():
            yield message.json

    def as_list(self):
        """
        Return restricted list of columns for list queries
        """
        deferred_cols = ("subject", 
                         "sender_id",
                         "recevier_id",
                         "content")

        options = [db.defer(col) for col in deferred_cols]
        return self.options(*options)

    def unread(self, user):

        msgs = self.filter( Message.receiver_id == user.id, Message.owner_id==user.id, Message.read==False ).all()
        return len(msgs)

        
class Message(db.Model, dbFunctions):
    __tablename__ = "messages"
    
    query_class = MessageQuery

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    sender = db.relationship("User", primaryjoin="User.id == Message.sender_id" )
    receiver_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    receiver = db.relationship("User", primaryjoin="User.id == Message.receiver_id" )

    # message owner, others should NOT delete the message
    owner_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    owner = db.relationship("User", primaryjoin="User.id == Message.owner_id" )

    subject = db.Column(db.String)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    __mapper_args__ = {'order_by' : id.desc()}

    class Permissions(Permissions):

        @cached_property
        def default(self):
            return Permission(UserNeed(self.owner.username)) 

        @cached_property
        def view(self):
            return self.default

        @cached_property
        def edit(self):
            return self.default

        @cached_property
        def delete(self):
            return self.default


    def __init__(self, owner,sender,receiver, subject, content):
        super(Message, self).__init__()
        self.owner_id     = owner.id
        self.sender_id    = sender.id
        self.receiver_id  = receiver.id
        self.subject = subject
        self.content = content
        self.content_html = YMK.convert(content)

    def __str__(self):
        return self.subject

    def __repr__(self):
        return u"<消息(%s:%s)>" % (self.id, self.subject)

    @cached_property
    def permissions(self):
        return self.Permissions(self)

    @cached_property
    def json(self):
        """
        Returns dict of safe attributes for passing into 
        a JSON request.
        """ 
        return dict(message_id=self.id,
                    subject=self.subject,
                    sender_id=self.sender.username,
                    receiver_id=self.receiver.username)

    @cached_property
    def access_name(self):
        return {
                 Message.PUBLIC : "public",
                 Message.FRIENDS : "friends",
                 Message.PRIVATE : "private"
               }.get(self.access, "public")
        
    def can_access(self, user=None):
        if self.access == self.PUBLIC:
            return True

        if user is None:
            return False

        if user.is_moderator or user.id == self.author_id:
            return True

        return self.access == self.FRIENDS and self.author_id in user.friends

    def _url(self, _external=False):
        return url_for('message.view', 
                       message_id=self.id, 
                       slug=self.slug, 
                       _external=_external)

    @cached_property
    def url(self):
        return self._url()

    @cached_property
    def permalink(self):
        return self._url(True)

    @cached_property
    def markdown(self):
        return tomarkdown(self.content or '')

    def slug(self):
        return slugify(self.subject or '')[:80]

    @cached_property
    def dateshow(self):
        return self.date_created.strftime("%c")
