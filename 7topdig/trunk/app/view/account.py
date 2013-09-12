# -*- coding: utf-8 -*- 
from flask import Blueprint, flash, request, current_app, \
    abort, redirect, url_for, session, jsonify, render_template
from flaskext.login import  LoginManager, login_user, logout_user,\
    UserMixin, AnonymousUser, confirm_login, fresh_login_required, \
    current_user
from flaskext.principal import identity_changed, Identity, \
    AnonymousIdentity, RoleNeed, UserNeed,  Permission,\
    identity_loaded, PermissionDenied
from flaskext.mail import Message
from app.forms import LoginForm, SignupForm, RecoverPasswordForm,\
    ResetPasswordForm

from app.models import User, save_action
from app.lib.permissions import auth
from app import mail, db
import setting
import uuid

"""
    定义account模块，在app.__init__.py中加载
"""
mod = Blueprint('account', __name__)

################################################################################
#
# Functions and Classes
#
################################################################################
from app.lib.weibo import APIClient

APP_KEY = '1253579791' # app key
APP_SECRET = '1dea3d521b1717d72bd5d1e2dca081c1' # app secret
CALLBACK_URL = 'http://www.7topdig.com/weibocallback' # callback url


@mod.route("/url/", methods=['GET', 'POST'])
def url():
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    myurl = client.get_authorize_url()
    return redirect(myurl)

################################################################################
#
# Routine to Account view
#
################################################################################
"""
   登录功能：
       1. 从表单获取用户输入
       2. 验证及查询相应的输入
       3. 验证成功
           3.1. 登录用户
           3.2. 建立身份标签, 告诉prinical用户身份改变
           3.3. 跳转到next_url或是用户首页
       4. 验证错误
           4.1. 跳转回登录界面
"""
@mod.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm(login=request.args.get("login", None),
                     next=request.args.get("next", None))

    # TBD: ensure "next" field is passed properly
    if form.validate_on_submit():
        user, authenticated = \
            User.query.authenticate(form.login.data,
                                    form.password.data)

        if user and authenticated:
            # Flask-Login
            login_user(user, remember = form.remember.data)
            
            # change identity
            identity=Identity(user.username)
            identity_changed.send(current_app._get_current_object(),
                                identity = identity)
            # next_url
            next_url = form.next.data
            if not next_url or next_url == 'home.index':
                next_url = url_for('user.posts', username=user.username)
                flash(u"登录成功", "successfully")
            return redirect(next_url)
        else:
            flash(u"账号或密码错误", "error")
    return render_template("account/login.html", form=form)

"""
    登出功能：
      1. 首先需要是已经登录的状态
      2. 使用 Flask-login: logout_user 登出
      3. 清空身份标签
      4. 跳转到next或是首页
"""
@mod.route("/logout/")
@auth.require(401)
def logout():
    # Remove the user information from the session
    logout_user()
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
           
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    flash(u"你已登出。", "successfully")
    return redirect(request.args.get('next') or url_for('home.index'))


"""
    用户注册功能：
    1. 显示用户注册表单
    2. 获取表单内容, 及验证成功
        2.1 修改数据库建立用户记录
        2.2 修改身份标签
        2.3 跳转到next或是用户首页
    3. 验证失败， 跳转到注册页面
"""
@mod.route("/signup/", methods=['GET', 'POST'])
def signup():
    form = SignupForm(next=request.args.get("next"))

    if form.validate_on_submit():        
        user = User()
        form.populate_obj(user)
        user.save()
        # Flask-Login
        login_user(user)
        
        # Flask-principal
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.username))

        flash(u"欢迎, %s" % user.username, "successfully")
        next_url = form.next.data
        if not next_url or next_url == request.path:
            next_url = url_for('user.posts', username=user.username)

        return redirect(next_url)
    return render_template("account/signup.html", form=form)

"""
    忘记密码功能：
    1. 显示忘记密码表单
    2. 获取表单内容Emal, 及验证成功
        2.1 生成activation_key
        2.2 给用户发送邮件
        2.3 跳转到找回密码页面
    3. 验证失败， 跳转到找回密码页面    
"""
@mod.route("/forgotpass/", methods=['GET', 'POST'])
def forgotpass():
    form = RecoverPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() 
        if user:
            # generate activation_key and save it in database
            user.activation_key = str(uuid.uuid4())
            user.save()
            
            # send recover email
            if setting.MAIL_ENABLE:
                body = render_template("emails/forgotpass.html",
                                       user=user)
                message = Message(subject=u"找回密码",
                                  body=body,
                                  sender=setting.ADMIN_MAIL,
                                  recipients=[user.email])
                mail.send(message)
                flash(u"邮件已发出", "successfully")
            else:
                flash(u"邮件服务器未开启，请联系管理员", "error")
            
            return redirect(url_for("account.forgotpass"))
        else:
            flash(u"对不起，没找到你的邮件", "error")
    return render_template("account/forgotpass.html", form=form)


"""
    重设密码功能：
    1. 根据activation_key找到该用户
    2. 显示用户重设密码表单
    3. 登出用户让用户使用新密码重新登录
        2.1 修改数据库建立用户记录
        2.2 修改身份标签
        2.3 跳转到next或是用户首页
    3. 验证失败， 跳转到注册页面
"""
@mod.route("/resetpass/", methods=['GET', 'POST'])
def resetpass():
    user = current_user
    if 'activation_key' in request.values and request.values['activation_key']:
        user = User.query.filter_by(
            activation_key=request.values['activation_key']).first()
    if user is None:
        abort(403)
    # setup new password
    form = ResetPasswordForm(activation_key=user.activation_key)
    if form.validate_on_submit():
        user.password = form.password.data
        user.activation_key = None
        user.save()
        flash(u"你的密码已成功重设。", "successfully")
        if current_user:
            logout_user()
        return redirect(url_for("account.login"))
    return render_template("account/resetpass.html", form=form)


"""
    关注好友功能：
    1. javascript 发送请求
    2. 查询到需要follow的用户记录
    3. 查询到自己的用户记录
    4. 修改记录并保存
"""
@mod.route("/follow/<int:user_id>/", methods=("POST",))
@auth.require(401)
def follow(user_id):
    user = User.query.get_or_404(user_id)

    if user == current_user:
        flash(u"你不能关注自己", "error")
        return jsonify(success=True, 
                       reload=True)

    current_user.follow(user)
    current_user.save()
    user.save()
    save_action('"' + current_user.username + '"' + u"关注 了 "+ '"' + user.username + '"')
    save_action(u"%s 关注了 %s" %(current_user.username, user.username)  ) 

#    body = render_template("emails/followed.html",
#                           user=user)
#    mail.send_message(subject=u"%s 关注了你" % current_user.username,
#                      body=body,
#                      sender=ADMIN_MAIL,
#                      recipients=[user.email])
    return jsonify(success=True,
                   reload=True)


"""
    取消关注功能：
    1. javascript 发送请求
    2. 查询到需要unfollow的用户记录
    3. 查询到自己的用户以及需要unfollow用户记录
    4. 修改记录并保存
"""
@mod.route("/unfollow/<int:user_id>/", methods=("POST",))
@auth.require(401)
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    current_user.unfollow(user)
    current_user.save()
    user.save()

    save_action('"' + current_user.username + '"' + u"关注 了 "+ '"' + user.username + '"')
    return jsonify(success=True,
                   reload=True)
    
