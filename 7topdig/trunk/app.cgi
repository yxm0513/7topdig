#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from app import app

from os import environ
environ['SERVER_PORT'] = "80"

app.config.update(
    SERVER_NAME="127.0.0.1:80"
)

CGIHandler().run(app)
