# -*- coding: utf-8 -*- 
from flask.ext.wtf import Form, TextField, SelectField, required, \
    SubmitField
from app.models import Category

################################################################################
#
# Form for user
#
################################################################################


class CategoryForm(Form):
    name = TextField(u"分类", validators=[
                     required(message=u'分类名是必须的')])
    try:
        choices=Category.query.all()
    except:
        choices=None
    father = SelectField(u"选择上级分类", choices)
    submit = SubmitField(u"发送")