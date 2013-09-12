# -*- coding: utf-8 -*-
from flaskext.sqlalchemy import BaseQuery
from app.lib.util import dbFunctions
from app import db


class Category(db.Model, dbFunctions):
    __tabename__ = "category"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    parent_id = db.Column(db.Integer, 
                          db.ForeignKey("category.id", ondelete='CASCADE'))

    parent = db.relation('Category', remote_side=[id])
    
    __mapper_args__ = {'order_by' : id.asc()}
    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
    