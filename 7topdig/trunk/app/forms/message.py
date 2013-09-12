# -*- coding: utf-8 -*-
from flaskext.wtf import Form, TextField, TextAreaField, RadioField, \
        validators, SubmitField, ValidationError, optional

class NewMessageForm(Form):
    sendto = TextField(u'收信人', [validators.required(message=u"发送人不能为空")])
    subject = TextField(u'标题', validators=[
            validators.required(message=u"标题不能为空"),
            validators.Length(min=4, max=100)])
    content = TextAreaField(u'内容', validators=[
            validators.required(message=u"内容不能为空"),
            validators.Length(min=6, max=2000)])
    submit = SubmitField(u'发送')

class ReplyMessageForm(Form):
    subject = TextField(u'标题', validators=[validators.required(message=u"标题不能为空"),
            validators.Length(min=4, max=100)])
    content = TextAreaField(u'内容', validators=[validators.required(message=u"内容不能为空"),
            validators.Length(min=6, max=2000)])
    submit = SubmitField(u'发送')

