# -*- coding: utf-8 -*-
from flaskext.sqlalchemy import SQLAlchemy, BaseQuery
from app.lib.util import DenormalizedText, dbFunctions
from app import db

# save page content with markdown or rst


class Page(db.Model, dbFunctions):
    __tablename__ = "pages"
    
    # supported types
    RST = 1
    MARKDOWN = 2
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    source = db.Column(db.Text)
    type = db.Column(db.Integer, default=1)
    
    def __init__(self, name = None, source = None, type = 1):
        self.name = name
        self.source = source
        self.type = type