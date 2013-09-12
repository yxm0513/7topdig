# -*- coding: utf-8 -*-
from flask import Markup
from sqlalchemy import types
from blinker import Namespace
from app import db, cache
import re, urlparse, functools 
from datetime import datetime
from docutils.core import publish_string
import markdown


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug. From http://flask.pocoo.org/snippets/5/"""
    result = []
    for word in _punct_re.split(text.lower()):
        #word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))


#markdown = functools.partial(markdown.markdown,
#                             safe_mode='remove',
#                             output_format="html")
#
#cached = functools.partial(cache.cached,
#                           unless= lambda: current_user is not None)


def tomarkdown(source):
    return Markup(markdown.markdown(source))

def torst(source):
    return Markup(publish_string(source=source, writer_name='html'))


def timesince(dt, default=None):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    
    if default is None:
        default = u"刚才"

    now = datetime.utcnow()
    diff = now - dt
    
    periods = (
        (diff.days / 365, u"年"),
        (diff.days / 30, u"月"),
        (diff.days / 7, u"周"),
        (diff.days, u"天"),
        (diff.seconds / 3600, u"小时"),
        (diff.seconds / 60, u"分钟"),
        (diff.seconds, u"秒"),
    )

    for period, unit in periods:
        if not period:
            continue
        unit = u"%d %s前" %(period, unit)
        return unit

    return default

def domain(url):
    """
    Returns the domain of a URL e.g. http://reddit.com/ > reddit.com
    """
    rv = urlparse.urlparse(url).netloc
    if rv.startswith("www."):
        rv = rv[4:]
    return rv

def basename(url):
    """
    Returns the basename of a URL e.g. http://reddit.com/xxx > xxx
    """
    rv = urlparse.urlparse(url)
    return rv.path

class DenormalizedText(types.MutableType, types.TypeDecorator):
    """
    Stores denormalized primary keys that can be 
    accessed as a set. 
    :param coerce: coercion function that ensures correct
                   type is returned

    :param separator: separator character
    """
    impl = types.Text

    def __init__(self, coerce=int, separator=" ", **kwargs):
        self.coerce = coerce
        self.separator = separator
        
        super(DenormalizedText, self).__init__(**kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            items = [str(item).strip() for item in value]
            value = self.separator.join(item for item in items if item)
        return value

    def process_result_value(self, value, dialect):
         if not value:
            return set()
         return set(self.coerce(item) \
                   for item in value.split(self.separator))
        
    def copy_value(self, value):
        return set(value)
    
    
class dbFunctions:
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.execute('PRAGMA foreign_keys=ON;')
        db.session.delete(self)
        db.session.commit()

    def commit(self):
        db.session.commit()