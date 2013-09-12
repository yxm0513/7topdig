#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from werkzeug.contrib.fixers import LighttpdCGIRootFix
from app import app


if __name__ == '__main__':
    WSGIServer(LighttpdCGIRootFix(app)).run()
