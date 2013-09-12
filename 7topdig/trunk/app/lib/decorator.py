# -*- coding: utf-8 -*-
"""
    lib/decorator.py
    ~~~~~~~~~~~~~~

    some decorator defined

"""
from functools import wraps
from flask import session, redirect, url_for, flash, request, make_response


def no_cache_header(f):
    @wraps(f)
    def do(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'private, post-check=0, pre-check=0, max-age=0'
        response.headers['Expires'] = '0'
        return response
    return do
