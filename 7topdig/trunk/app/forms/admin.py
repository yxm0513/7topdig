# -*- coding: utf-8 -*- 
from flask.ext.wtf import Form, validators, required, TextField, \
        PasswordField, SubmitField, equal_to, file_required, \
         email, TextAreaField, FileField, file_allowed
from app import db

################################################################################
#
# Form for admin
#
################################################################################
class MailAllForm(Form):
    subject = TextField(u'标题', [required()])
    message = TextAreaField(u'内容', [required()])
    submit = SubmitField(u'发送')