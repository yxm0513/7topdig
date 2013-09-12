# -*- coding: utf-8 -*- 
from flask import Flask, render_template, request, jsonify, \
    redirect, url_for, flash, make_response
from flask_debugtoolbar import DebugToolbarExtension
from flaskext.babel import Babel
from flaskext.mail import Mail
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy.interfaces import PoolListener
from flaskext.principal import Principal, RoleNeed, identity_loaded, \
    AnonymousIdentity
from flaskext.login import LoginManager
from flaskext.cache import Cache
from flaskext.uploads import UploadSet, IMAGES, configure_uploads
from blinker import Namespace
import setting
import sys


app = Flask(__name__)
app.config.from_object(setting)

app.debug = True
toolbar = DebugToolbarExtension(app)

mail = Mail(app)
babel = Babel(app)
cache = Cache(app)
#db = SQLAlchemy(app)
principals = Principal(app)
login_manager = LoginManager()
login_manager.setup_app(app)
userimage = UploadSet('userimage', IMAGES)
configure_uploads(app, (userimage))

# setting
# fix issue of unicode
reload(sys)
sys.setdefaultencoding("utf-8")

# fix issue of forerign_keys problem for SQLite
#db.session.execute('PRAGMA foreign_keys=ON;')
class SQLiteForeignKeysListener(PoolListener):
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')


class StrictSQLAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        super(StrictSQLAlchemy, self).apply_driver_hacks(app, info, options)
        if info.drivername == 'sqlite':
            options.setdefault('listeners', []).append(SQLiteForeignKeysListener())

db = StrictSQLAlchemy(app)

################################################################
#
# add filters for template
#
################################################################
from app.lib.util import timesince, basename, torst, tomarkdown
app.jinja_env.filters['timesince'] = timesince
app.jinja_env.filters['basename'] = basename
app.jinja_env.filters['rst'] = torst
app.jinja_env.filters['markdown'] = tomarkdown


################################################################
#
# add basic routes
#
################################################################
signals = Namespace()

comment_added = signals.signal("comment-added")
comment_deleted = signals.signal("comment-deleted")


@comment_added.connect
def comment_added(post):
    post.num_comments += 1
  
################################################################
#
# OAuth
#
################################################################


################################################################
#
# add basic setup
#
################################################################
from app.models import User

@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(id)
    except:
        return None

@identity_loaded.connect
def on_identity_loaded(sender, identity):
    # find the role for user
    try:
        identity.provides = User.query.filter(User.username.like(identity.name)).first().provides
    except:
        identity = AnonymousIdentity


################################################################
#
# add basic routes
#
################################################################
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("image/favicon.ico")

#@app.route('/sitemap.xml', methods=['GET'])
#def sitemap():
#  response = make_response(open('sitemap.xml').read())
#  response.headers["Content-type"] = "text/plain"
#  return response

@app.errorhandler(401)
def notauthorized(error):
    if request.is_xhr:
        return jsonify(error='抱歉,没有权限', redirect_url=url_for("account.login"))
    else:
        flash(u"抱歉,没有权限", "error")
        return redirect(url_for("account.login", next=request.path))

# register error handler
@app.errorhandler(404)
def page_not_found(error):
    if request.is_xhr:
        return jsonify(error=u'抱歉, 页面未找到！')
    else:
        return render_template("error/404.html", error=error)

@app.errorhandler(403)
def forbidden(error):
    if request.is_xhr:
        return jsonify(error=u'抱歉,没有权限.', redirect_url=url_for("account.login"))
    else:
        flash(u"抱歉,没有权限", "error")
        return redirect(url_for("account.login", next=request.path))

@app.errorhandler(500)
def server_error(error):
    if request.is_xhr:
        return jsonify(error=u'抱歉, 系统错误.')
    else:
        return render_template("error/500.html", error=error)


################################################################
#
# add Blueprints
#
################################################################
from view import home
from view import account
from view import admin
from view import user
from view import post
from view import feeds
from view import comment
from view import api
from view import test
from view import message

app.register_blueprint(home.mod)
app.register_blueprint(account.mod, url_prefix='/account')
app.register_blueprint(admin.mod, url_prefix='/admin')
app.register_blueprint(user.mod, url_prefix='/user')
app.register_blueprint(post.mod, url_prefix='/post')
app.register_blueprint(feeds.mod, url_prefix='/feeds')
app.register_blueprint(comment.mod, url_prefix='/comment')
app.register_blueprint(api.mod, url_prefix='/api')
app.register_blueprint(test.mod, url_prefix='/test')
app.register_blueprint(message.mod, url_prefix='/message')
