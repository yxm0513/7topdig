# -*- coding: utf-8 -*-
from app.lib.util import dbFunctions
from app import db


class Search(db.Model, dbFunctions):
    __tablename__ = "searchs"
    id = db.Column(db.Integer, primary_key=True)
    words = db.Column(db.String(200), unique=True)
    times = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.words = self.words
        self.times = self.times
