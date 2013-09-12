# -*- coding: utf-8 -*-
from flaskext.wtf import Form, TextField, TextAreaField, RadioField, \
        SubmitField, ValidationError, optional, required, url

from app.models import Post
from app import db

class PostForm(Form):
    title = TextField(u"标题", validators=[
                      required(message=u"标题不能为空")], id = "post_title")

    link = TextField(u"链接", default="http://", validators=[
                     optional(),
                     url(message=u"必须是个有效的链接")], id = "post_link")
    description = TextAreaField(u"描述", id = "post_description")
    tags = TextField(u"标签(用逗号分隔)", id = "post_tags")
    access = RadioField(u"谁可以查看?", 
                        default=Post.PUBLIC, 
                        coerce=int,
                        choices=((Post.PUBLIC, u"任何人"),
                                 (Post.FRIENDS, u"好友"),
                                 (Post.PRIVATE, u"只有自己")))
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        self.post = kwargs.get('obj', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def validate_link(self, field):
        posts = Post.query.public().filter_by(link=field.data)
        if self.post:
            posts = posts.filter(db.not_(Post.id==self.post.id))
        if posts.count():
            raise ValidationError, u"这个链接已经有人提交了"

class LoadPostForm(Form):
    douban = TextField(u"来自豆瓣:", validators=[
                     url(message=u"必须是个有效的链接")], id="link_submit")
    submit = SubmitField(u"加载", id="load_data")

class CommentForm(Form):
    comment = TextAreaField(validators=[
                            required(message="内容不能为空")])
    submit = SubmitField(u"提交")
    cancel = SubmitField(u"取消")

class CommentAbuseForm(Form):
    complaint = TextAreaField("抱怨", validators=[
                              required(message= "你有些啥抱怨呢？")])
    submit = SubmitField(u"提交")
