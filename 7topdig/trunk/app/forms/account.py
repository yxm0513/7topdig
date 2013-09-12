# -*- coding: utf-8 -*- 
from flask.ext.wtf import Form, TextField, PasswordField, BooleanField,\
         SubmitField, validators, required, equal_to, file_required, \
         email, TextAreaField, HiddenField, RecaptchaField, regexp, \
         ValidationError
from flask.ext.wtf.file import FileField, file_required, file_allowed
from app import db
from app.models.account import User


USERNAME_RE = r'^[\w.+-]+$'
is_username = regexp(USERNAME_RE, message=u"你只能使用字符，数字和下划线")

################################################################################
#
# Form for account
#
################################################################################
class LoginForm(Form):
    next = HiddenField()
    remember = BooleanField(u"在这台电脑记住我")
    login = TextField(u"账号：", validators=[ required(message=\
                               u"你必须提供一个用户名或是 Email")])
    password = PasswordField(u"密码：", [required()])
    submit = SubmitField(u"登录")


class UserForm(Form):
    username = TextField(u"用户名", validators=[
                         required(message=u"用户名是必须的"), 
                         is_username])
    password = PasswordField(u"密码", validators=[
                             required(message=u"密码是必须的")])
    email = TextField(u"Email", validators=[
                      required(u"邮箱地址是必须的"), 
                      email(message=u"必须是一个邮箱哦")])
    submit = SubmitField(u"添加")

    def validate_username(self, field):
        user = User.query.filter(User.username.like(field.data)).first()
        if user:
            raise ValidationError, u"用户名已被使用"

    def validate_email(self, field):
        user = User.query.filter(User.email.like(field.data)).first()
        if user:
            raise ValidationError, u"邮箱已被使用"


class SignupForm(UserForm):
    next = HiddenField()
    username = TextField(u"用户名", validators=[
                         required(message=u"用户名是必须的"), 
                         is_username])
    password = PasswordField(u"密码", validators=[
                             required(message=u"密码是必须的")])

    password_again = PasswordField(u"密码 <small>(再一次)</small>", validators=[
                                   equal_to("password", message=\
                                            "密码不匹配")])
    email = TextField(u"Email", validators=[
                      required(u"邮箱地址是必须的"), 
                      email(message=u"必须是一个邮箱哦")])
    submit = SubmitField(u"注册")


class RecoverPasswordForm(Form):
    email = TextField(u"你的Email", validators=[email(message=u"必须是有效Email.")])
    submit = SubmitField(u"提交")

class ResetPasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField(u"新密码", validators=[
                             required(message=u"新密码是必须的")])
    password_again = PasswordField(u"密码 <small>(再一次)</small>", validators=[
                                   equal_to("password", message=\
                                            u"密码不匹配")])
    submit = SubmitField(u"保存")



