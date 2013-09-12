# -*- coding: utf-8 -*-
from flask import url_for, Markup
from flaskext.sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import func
from flaskext.principal import RoleNeed, UserNeed, Permission
from flaskext.login import UserMixin
from datetime import datetime
import random, os

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import cached_property
from app.lib.permissions import Permissions, null
from app.lib.util import DenormalizedText, dbFunctions
from app import db, userimage
import setting



#######################################################################
#
#  Model for Account
#
#######################################################################
class UserQuery(BaseQuery):
    def from_identity(self, identity):
        """
        Loads user from flaskext.principal.Identity instance and
        assigns permissions from user.

        A "user" instance is monkeypatched to the identity instance.

        If no user found then None is returned.
        """
        try:
            user = self.get(int(identity.name))
        except ValueError:
            user = None

        if user:
            identity.provides.update(user.provides)
        identity.user = user
        return user
 
    def authenticate(self, login, password):        
        user = self.filter(db.or_(User.username==login,
                                  User.email==login)).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated
    
    def hottest(self):
        return self.order_by(User.last_action.desc())
    
    def random(self, number):
        return self.order_by(func.random()).limit(number).all()
        


class User(db.Model, UserMixin, dbFunctions):
    __tablename__ = "users"

    query_class = UserQuery

    # user roles
    GUEST = 0
    MEMBER = 100
    MODERATOR = 200
    ADMIN = 300

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    karma = db.Column(db.Integer, default=0)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    activation_key = db.Column(db.String(80), unique=True)
    role = db.Column(db.Integer, default=MEMBER)
    receive_email = db.Column(db.Boolean, default=False)
    email_alerts = db.Column(db.Boolean, default=False)
    followers = db.Column(DenormalizedText)
    following = db.Column(DenormalizedText)
    _password = db.Column("password", db.String(80))

    class Permissions(Permissions):
        @cached_property
        def send_message(self):
            if not self.receive_email:
                return null

            needs = [UserNeed(username) for username in self.friends]
            if not needs:
                return null

            return Permission(*needs)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.followers = self.followers or set()
        self.following = self.following or set()

    def __str__(self):
        return self.username

    def __repr__(self):
        return "<%s>" % self

    @cached_property
    def permissions(self):
        return self.Permissions(self)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)

    password = db.synonym("_password", 
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    @cached_property
    def provides(self):
        needs = [RoleNeed('authenticated'),
                 UserNeed(self.username)]

        if self.is_moderator:
            needs.append(RoleNeed('moderator'))

        if self.is_admin:
            needs.append(RoleNeed('admin'))
        
        return needs

    @cached_property
    def num_followers(self):
        if self.followers:
            return len(self.followers)
        return 0

    @cached_property
    def num_following(self):
        return len(self.following)

    def is_following(self, user):
        return user.id in self.following

    @property
    def num_unread_message(self):


        from app.models import Message
        unread = Message.query.unread(self)
        return unread  


    @property
    def friends(self):
        return self.following.intersection(self.followers)

    def is_friend(self, user):
        return user.id in self.friends

    def get_friends(self):
        return User.query.filter(User.id.in_(self.friends))

    def follow(self, user):
        user.followers.add(self.id)
        self.following.add(user.id)

    def unfollow(self, user):
        if self.id in user.followers:
            user.followers.remove(self.id)

        if user.id in self.following:
            self.following.remove(user.id)

    def get_following(self):
        """
        Return following users as query
        """
        return User.query.filter(User.id.in_(self.following or set()))

    def get_followers(self):
        """
        Return followers as query
        """
        return User.query.filter(User.id.in_(self.followers or set()))

    @property
    def is_moderator(self):
        return self.role >= self.MODERATOR

    @property
    def is_admin(self):
        return self.role >= self.ADMIN


    def avatar_url(self, type=None):
        file = None
        file_url=None
        if type:
            file = '/%s_%s.jpg'% (self.username, type)
            file_url = 'avatar/%s_%s.jpg'% (self.username, type)
        else:
            file = '/%s.jpg'% self.username
            file_url = 'avatar/%s.jpg'% self.username
        path = setting.AVATAR_PATH + file
        if os.path.exists(path):
            return url_for("static", filename=file_url)
        else:
            return url_for("static", filename="avatar/default_small.png")

#from app.models import Post
class Favorites(db.Model, dbFunctions):
    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    #post_id = db.Column(db.Integer, db.ForeignKey(Post.id, ondelete='CASCADE'), nullable=False)
    author = db.relation(User, innerjoin=True, lazy="joined")
    #post = db.relation(Post, innerjoin=True, lazy="joined")


class UserImage(db.Model, dbFunctions):
    __tablename__ = "images"

    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    filename = db.Column(db.String(60))
    user = db.relation(User, innerjoin=True, lazy="joined")
    
    def __init__(self, filename, user):
        self.filename = filename
        self.user = user

    def __repr__(self):
        return '<Photo %r>' % self.filename

    @property
    def url(self):
        return(userimage.url(self.filename))

    def save(self):
        db.session.add(self)
        db.session.commit()
