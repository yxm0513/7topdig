# -*- coding: utf-8 -*- 
from flask.ext.wtf import Form, validators, required, TextField, \
        PasswordField, SubmitField, TextAreaField, SelectField

class PageEditForm(Form):
    types = [('1', 'RST'), ('2','Markdown')]
    rawtext = TextAreaField(u"编辑", id="page_edit")
    texttype = SelectField(u"选择文件类型", choices = types, default = '1')
    save = SubmitField(u"保存")
    preview = SubmitField(u"预览")
    cancel = SubmitField(u"取消")

    def set_default_text(self, text=None):
        self.rawtext.data = text