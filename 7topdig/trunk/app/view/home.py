# -*- coding: utf-8 -*- 
from flask import Blueprint, render_template, url_for,\
    flash, g, redirect, request, abort, jsonify
from flaskext.login import current_user
from app.models import Post, User, Tag, Page, Action, Search, Category, save_action
from app.forms import PostForm, LoadPostForm, ContactForm, PageEditForm
from flaskext.mail import Message
from app import app, mail, cache, db
from app.lib.permissions import auth
from feedparser import parse
from urlparse import urlparse
import setting
import re


"""
    定义home模块，在app.__init__.py中加载
"""
mod = Blueprint('home', __name__)

################################################################################
#
# Routine to Home view
#
################################################################################
"""
    首页：
    Categories
"""
@mod.route("/")
@mod.route('/index')
def index():
    categories = Category.query.all();
    return render_template("home/index.html", categories = categories)


"""
        默认按照vote数排行
"""
@mod.route('/list')
@mod.route("/<int:page>/")
#@cache.cached()
#@keep_login_url
def list(page=1):
    if current_user.is_anonymous: 
        page_obj = Post.query.best().restricted().as_list().\
            paginate(page, per_page=Post.PER_PAGE)
    else:
        page_obj = Post.query.hottest().restricted(current_user).as_list().\
            paginate(page, per_page=Post.PER_PAGE)
    page_url = lambda page: url_for("home.list", page=page)

    return render_template("home/list.html", 
                           page_obj=page_obj, 
                           page_url=page_url)

"""
    最新：
            最新的投递，或者是最新vote的Post
"""
@mod.route("/latest/")
@mod.route("/latest/<int:page>/")
#@cached()
#@keep_login_url
def latest(page=1):
    if current_user.is_anonymous: 
        page_obj = Post.query.restricted().as_list().\
            paginate(page, per_page=Post.PER_PAGE)
    else:
        page_obj = Post.query.restricted(current_user).as_list().\
            paginate(page, per_page=Post.PER_PAGE)
    page_url = lambda page: url_for("home.latest", page=page)
    return render_template("home/latest.html", 
                           page_obj=page_obj, 
                           page_url=page_url)

"""
    最热：
            一段时间内vote最多的Post
"""
@mod.route("/hottest/")
@mod.route("/hottest/<int:page>/")
#@cached()
#@keep_login_url
def hottest(page=1):
    if current_user.is_anonymous: 
        page_obj = Post.query.hottest().as_list().\
            paginate(page, per_page=Post.PER_PAGE)
    else:
        page_obj = Post.query.hottest().restricted(current_user).as_list().\
            paginate(page, per_page=Post.PER_PAGE)
    page_url = lambda page: url_for("home.hottest", page=page)
    return render_template("home/hottest.html", 
                           page_obj=page_obj, 
                           page_url=page_url)

"""
    分数为负：
    deadpool Post
"""
@mod.route("/deadpool/")
@mod.route("/deadpool/<int:page>/")
#@cached()
#@keep_login_url
def deadpool(page=1):
    page_obj = Post.query.deadpooled().as_list().\
        paginate(page, per_page=Post.PER_PAGE)
    page_url = lambda page: url_for("home.deadpool", page=page)
    return render_template("home/index.html", 
                           page_obj=page_obj, 
                           page_url=page_url)

"""
    提交一个新的Post：
    1. 需要首先登陆
    2. 提交内容
    3. 跳转到最新页面
"""
@mod.route("/submit/", methods=['GET', 'POST'])
@auth.require(401)
def submit():
    form = PostForm()
    loadform = LoadPostForm()
    category_form = CatgoryForm()
    if form.validate_on_submit():
        post = Post()
        form.populate_obj(post)
        post.author=current_user
        post.save()
        flash(u"多谢你的提交", "successfully")
        # save the action
        save_action(u"提交了条目 " + u'"' + post.title + u'"' )
        return redirect(url_for("home.latest"))
    return render_template("home/submit.html", form=form, loadform = loadform, category_form = category_form )

"""
    搜索：
    1. 提交搜索内容
    2. 查询结果
    3. 显示结果页面
"""
@mod.route("/search")
@mod.route("/search/<int:page>")
#@keep_login_url
def search(page=1):
    keywords = request.args.get("keywords", '').strip()

    if not keywords:
        return redirect(url_for("home.index"))
    
    s = Search.query.filter_by(words = keywords).first()
    if s:
        #org.update({"words":keywords, "times":org.times + 1 })
        s.times = s.times + 1
        s.save()
    else:
        n = Search()
        n.words = keywords
        n.times = 1
        n.save()        
    
    page_obj = Post.query.search(keywords).as_list().\
        paginate(page, per_page=Post.PER_PAGE)
    if page_obj.total == 1:
        post = page_obj.items[0]
        return redirect(post.url)
    page_url = lambda page: url_for('home.search', 
                                    page=page,
                                    keywords=keywords)

    return render_template("home/search.html",
                           page_obj=page_obj,
                           page_url=page_url,
                           keywords=keywords)

"""
    标签：
    1. 查询所有标签
    2. 显示结果页面
"""
@mod.route("/tags/")
#@cached()
#@keep_login_url
def tags():
    tags = Tag.query.cloud()
    return render_template("home/tags.html", tags=tags)

"""
    标签：
    1. 查询标签
    2. 显示该标签的结果页面
"""
@mod.route("/tag/<slug>/")
@mod.route("/tag/<slug>/<int:page>/")
#@cached()
#@keep_login_url
def tag(slug, page=1):
    tag = Tag.query.filter_by(slug=slug).first_or_404()

    page_obj = tag.posts.as_list().\
                    paginate(page, per_page=Post.PER_PAGE)

    page_url = lambda page: url_for('home.tag',
                                    slug=slug,
                                    page=page)

    return render_template("home/tag.html", 
                           tag=tag,
                           page_url=page_url,
                           page_obj=page_obj)

"""
    联系我们：
    1. 发送邮件到管理员的邮箱
"""
@mod.route("/contact/", methods=['GET', 'POST'])
#@keep_login_url
def contact():
    user = None
    if user:
        form = ContactForm(name=user.username,
                           email=user.email)
    else:
        form = ContactForm()
    if form.validate_on_submit():
        admins = app.config.get('ADMINS', [])

        from_address = "%s <%s>" % (form.name.data, 
                                    form.email.data)

        if admins and setting.MAIL_ENABLE:
            message = Message(subject=form.subject.data,
                              body=form.message.data,
                              recipients=admins,
                              sender=from_address)
            mail.send(message)
            flash(u"谢谢，你的邮件已发出", "successfully")
        else:
            flash(u"邮件服务器未开启，请联系管理员", "error")
        return redirect(url_for('home.index'))
    return render_template("home/contact.html", form=form)


"""
    显示douban相关信息
"""
@mod.route('/load_data')
def load_data(link=None):
    link = request.args.get('link')
    p = re.compile(r'(?P<id>\d+)')
    r = p.search(link)
    id = r.group("id")
    if id:
        book = parse(setting.DOUBAN_API_PATH + id)
        info = book.entries[0]
        title = None
        summary = None
        tags = { 'name' : None}
        if hasattr(info, 'title'):
            title = info.title
        if hasattr(info, 'summary'):
            summary = info.summary            
        if hasattr(info, 'db_tag'):
            tags = info.db_tag            
        return jsonify(title = title,
                       summary = summary,
                       tags =  tags, 
                       link = setting.DOUBAN_BOOK_PATH + id)
    else:
        return jsonify(title=None)

@mod.route('/updatelatestinfo')
def updatelatestinfo():
    actions = Action.query.order_by(Action.time.desc()).limit(30)
    return render_template("home/_latest_info.html", actions = actions)


@mod.route("/page/<name>", methods = ['GET','POST'])
def page(name="MainPage"):
    page = Page.query.filter_by(name=name).first()
    form = PageEditForm()
    action = request.args.get('action')
    if request.method == 'POST':
        if 'save' in request.form:
            if page:
                page.source = form.rawtext.data
                page.type = form.texttype.data
                page.save()
            else: 
                page = Page(name=name, source=form.rawtext.data)
                page.save()
                save_action(u"修改页面" + u'"' + page.title + u'"' )
            return redirect(url_for('home.page', name=name))
        elif 'preview' in request.form:
            form = PageEditForm(request.form)
            preview = form.rawtext.data
            return render_template("home/editpage.html", form=form, page = page, preview = preview) 
        else:
            # for cancel
            return render_template("home/page.html", page=page)          
    else:
        if action == "edit":
            if not page:
                flash(u"建立一个新页面")
                form.set_default_text(text=u"在这里编辑内容")
                return render_template("home/editpage.html", form=form, page = page)
            else:
                source = page.source
                form.set_default_text(text=source)
                return render_template("home/editpage.html", form=form, page = page)
        # render to template
        return render_template("home/page.html", page=page)


"""
    罗列信息：
    1. 免责条款
    2. 关于我们
    3. 帮助信息
    4. API
"""
@mod.route("/rules")
def rules():
    page = Page.query.filter(Page.name == u"免责条款").first()
    if not page:
        abort(404)
    else:
        return render_template("home/page.html", page = page)

@mod.route('/about')
def about():
    page = Page.query.filter(Page.name == u"关于我们").first()
    if not page:
        abort(404)
    else:
        return render_template("home/page.html", page = page)

@mod.route('/help')
def help():
    page = Page.query.filter(Page.name == u"帮助").first()
    if not page:
        abort(404)
    else:
        return render_template("home/page.html", page = page)

@mod.route("/api")
def api():
    page = Page.query.filter(Page.name == u"API").first()
    if not page:
        abort(404)
    else:
        return render_template("home/page.html", page = page)
