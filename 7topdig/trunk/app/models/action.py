# -*- coding: utf-8 -*-
from flask import url_for, Markup
from flaskext.sqlalchemy import SQLAlchemy, BaseQuery
from werkzeug import cached_property
from app.lib.permissions import Permissions, null
from app.lib.util import dbFunctions
from app import db
from .account import User
import setting
from datetime import datetime
from flaskext.login import current_user

class Action(db.Model, dbFunctions):
    __tablename__ = "actions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    action = db.Column(db.String(200))
    time = db.Column(db.DateTime, default=datetime.utcnow)
   
    user = db.relationship(User, backref='user', lazy="joined")
   
    def __init__(self, action= None, user = None):
        self.action = action
        self.user = user
        
    @cached_property
    def dateshow(self):
        return self.time.strftime("%c")
    
    
def save_action(name = ""):
    author = current_user
    action = Action(name, author)
    action.save()
