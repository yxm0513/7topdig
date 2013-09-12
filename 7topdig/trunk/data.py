# -*- coding: utf-8 -*-
from app import db
from app.models import User, Post, Page, Category
from optparse import OptionParser
from feedparser import parse
import setting
import re

def infoprint(message = None, status = 'info'):
    print status.upper() + ": " + message 

def createUser(username=None, password=None, email=None, role=100):
    """
         创建新用户
    """
    if username is None:
            user = User.query.filter(User.username==username).first()
            if user is not None:
                infoprint(u"Username %s is already taken" % username, 'error')
            else:
                return None

    if email is None:
            user = User.query.filter(User.email==email).first()
            if user is not None:
                infoprint(u"Email %s is already taken" % email , 'error')
            else:
                return None
    user = User(username=username,
                email=email,
                password=password,
                role=role)
    user.save()
    return user
    
    
def createPost(author=None, title=None, description=None, link=None, \
               date_created = None, score = 0, num_comments = 0, votes = None,\
                access = None, tags = None):
    """
         创建一个新的Post
        id = db.Column(db.Integer, primary_key=True)
        author_id = db.Column(db.Integer, 
                              db.ForeignKey(User.id, ondelete='CASCADE'), 
                              nullable=False)
        title = db.Column(db.Unicode(200))
        description = db.Column(db.String)
        link = db.Column(db.String(250))
        date_created = db.Column(db.DateTime, default=datetime.utcnow)
        score = db.Column(db.Integer, default=1)
        num_comments = db.Column(db.Integer, default=0)
        votes = db.Column(DenormalizedText)
        access = db.Column(db.Integer, default=PUBLIC)
        
        _tags = db.Column("tags", db.String)
        
        author = db.relation(User, innerjoin=True, lazy="joined")
    """
    post = Post(author_id=author.id,
                title=title,
                description=description,
                link=link,
                date_created = date_created,
                score = score,
                num_comments = num_comments,
                votes = votes,
                access = access,
                tags =tags)
    post.save()
    return post

"""
    初始化一些数据库
"""
def initdb():
    # fix for CASCADE not work issue
    db.session.execute('PRAGMA foreign_keys=ON;')
    try:
        db.create_all()
    except:
        db.drop_all()
    # add some records
    try:
        # add some users
        admin = createUser(u'admin', u'111111', u'simon.yang.sh@gmail.com', 300)
        simon = createUser(u'simon', u'111111', u'simon.yang@emc.com', 300)
        ray = createUser(u'ray', u'111111', u'ray.chen@emc.com')
        yxm0513 = createUser(u'yxm0513', u'111111', u'yxm0513@gmail.com', 200)
        gonglidi = createUser(u'gonglidi', u'111111', u'gonglidi@gmail.com')
        infoprint(u"create users table successfully.", 'successfully')

        # add some tags
        
        
        # search function
        search_url = 'http://api.douban.com/book/subjects?tag=python&max-results=200'
        books = parse(search_url)
        link = ''
        ID = []
        for e in books['entries']:
            if hasattr(e, 'link'):
                link = e.link
                p = re.compile(r'(?P<id>\d+)')
                r = p.search(link)
                id = r.group("id")
                ID.append(id)
        # add some book info from douban
        #ID = range(11505944, 11505960)
        for id in ID:
            book = parse(setting.DOUBAN_API_PATH + '/' + str(id))
            title = u''
            summary = u''
            tags = u''
            for e in book['entries']:
                if hasattr(e, 'title'):
                    title = e.title
                if hasattr(e, 'summary'):
                    summary = e.summary
                if hasattr(e, 'db_tag'):
                    if 'python' in e.db_tag.get('name').lower():
                        tags = e.db_tag.get('name')
                    else:
                        tags = e.db_tag.get('name') + ',python'
                post = createPost(simon, title, summary, tags=tags)
        infoprint(u"create posts table successfully.", 'successfully')  
        
        
        # add some page info
        rules_source = u"""
免责条款
=================================
:作者: simon.yang.sh <at> gamil <dot> com   
:版本: 0.1 of 2012/07

关于提交内容
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    * 如果你觉得有什么破坏条款的请 联系我们
    * 如果你愿意监督我们的内容，联系我们吧。
"""
        rules = Page(u"免责条款", rules_source)
        rules.save()
        about_source = u"""
===================================
关于我们
===================================


我们想做的是什么呢，简单的说就是
    
   *用 digg的方式给用户提供一个读书的榜单.*

缘由：

   通常我们会在很多论坛看见很多新手问类似于，“我想学python,各位大侠有没有好的书推荐”， 我们为什么不用digg的方式来给我们构建这么的榜单呢，让大家的投票说话。

我们有什么不一样：
 * 我们只做过滤工作，给用户需要的信息 -- 做信息的减法
 * 豆瓣也有书，但不是一个榜单。
 * 我们很社会化，可构建圈子，评论也需要言简意赅，字数被限制在140个字符
 * 未来期望构建知识的架构图，树形的展示知识的架构，给学习者直观的知道，学习者可以由浅入深的研究自己希望的课题。

"""
        about = Page(u"关于我们", about_source)
        about.save()
        api_source = u"""
API
===================================
  * Coming Soon!!!
"""
        api = Page(u"API", api_source)
        api.save()
        help_source = u"""
帮助
===================================
  * Coming Soon!!!
"""
        helppage = Page(u"帮助", help_source)
        helppage.save()
        infoprint(u"create pages table successfully.", 'successfully')  
    except Exception as e:
        infoprint(u"create tables failed: %s" % e, 'error')

    cate1 = Category(name=u"计算机")
    cate2 = Category(name=u"编程", parent=cate1)
    cate1.save()
    cate2.save()
    infoprint(u"create categories table successfully.", 'successfully')  



"""
       删除数据库
"""
def dropdb():
    db.drop_all()
    infoprint(u"drop database", 'successfully')
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", "--create", action="store_true", dest="create",
                      help="create database")
    parser.add_option("-d", "--drop", action="store_true", dest="drop",
                      help="drop database")
    
    (options, args) = parser.parse_args()   
    if options.create:
        initdb()
    elif options.drop:
        dropdb()
    else:
        parser.print_help()
        
