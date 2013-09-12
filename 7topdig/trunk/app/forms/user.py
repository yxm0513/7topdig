# -*- coding: utf-8 -*- 
from flask.ext.wtf import Form, TextField, PasswordField, BooleanField,\
         SubmitField, validators, required, equal_to, file_required, \
         email, TextAreaField, HiddenField, RecaptchaField, regexp, \
         ValidationError, FileField, file_allowed
from app.models import User
from app import db, userimage


################################################################################
#
# Form for user
#
################################################################################
class ContactForm(Form):
    name = TextField(u"你的姓名", validators=[
                     required(message=u'姓名是必须的')])
    email = TextField(u"你的邮件", validators=[
                      required(message=u"邮件是必须的"),
                      email(message=u"需要是有效的邮箱地址")])
    subject = TextField(u"标题", validators=[
                        required(message=u"需要有标题")])
    message = TextAreaField(u"内容", validators=[
                            required(message=u"内容是必须的")])
    submit = SubmitField(u"发送")

class MessageForm(Form):
    subject = TextField(u"标题", validators=[
                        required(message=u"需要有标题")])

    message = TextAreaField(u"内容", validators=[
                            required(message=u"需要有内容")])

    submit = SubmitField(u"发送")

class SearchUserForm(Form):
    search = TextField(u'查找用户', validators=[
                     required(message=u'信息是必须的')])
    submit = SubmitField(u"搜索")


class UploadImageForm(Form):
    image = FileField(u"上传你的头像", validators=[file_allowed(userimage, u"只允许使用图片")])
    submit = SubmitField(u"上传", id="upload_submit")


