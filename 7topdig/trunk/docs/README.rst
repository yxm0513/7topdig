topdig 
=================================

:Authors: simon.yang.sh <at> gamil <dot> com   
:Version: 0.1 of 2012/07

.. contents::

简述
~~~~~~~~~~
简单的说我们是要提供给用户学习某方面书籍的排行榜。
	* 实现上类似于Digg, 只是推荐的是学习的材料，书~~
	* 给用户一个搜索框： earch : 我要学（______） ==> GO
		* List 相关的主题，主题之间有一定相关性(你可能喜欢：)
		* List 出书的排名   可以顶和踩， 然后你还可以加条目，以及评论
	* index.html
		* 注册： 加入我们
		* 及时更新谁喜欢什么，正在学习什么，或者想学什么	
	

计划分以下两步来实现:

* 研究和实现web通用技术，其中包括：

  * Flask : A micro web framework
  * Extentions for Flask: SQLAlchmey, Login, Testing, Uploads, debuggertoolbar
  * SQLite3
  * jQuery/CSS/XHTML

* 融合上述技术，实现Ims

  * Login/Logout/Register  -- Basic Done
  * Item CURD
  * Management 
  * Deplyment  -- Done
  * Tags, top tags
  * Search
	
扩展开的话，可以是
* 我想干什么？
  * 学车 
	* 给你驾校信息，联系人信息，顶和踩，
	* 远近，周围是不是也有人想学
  * 运动：打球，游泳
	* 附近是不是也有人想打球，可以相约一起活动
	* 附近的场馆信息
  * 唱歌
  * 看电影
    * 给出最近上映的电影信息，位置，价格啥的
    * 看话剧 。。。。
  * 去哪里 
	* mashup 相关的信息， 酒店，行程，机票，火车。
		
风格参考：
	CSS: zhiliao.in
	支持各种社交网络的登录
	Login: 
		http://packages.python.org/Flask-Principal/
		http://packages.python.org/Flask-Security/
		http://packages.python.org/Flask-Auth/quickstart.html
	Comment:
		http://disqus.com/api/applications/1550446/
依赖
~~~~~~~~

  * Python
  * SQLite3
  * SQLAlchmey
  * feedparser
  * simplejson
  * python-wtforms
  * python-markdown
  * python-profiler: pstats

    commands::

    sudo  apt-get install python sqlite3 python-sqlalchemy python-feedparser python-wtforms python-markdown python-profiler
 

部署
~~~~~~~~

  * Sanity Check run.py

    * download source code
    * install all above requirements
    * do setup in settings, like project directory
    * run #python run.py

  * lighttp/flup/fcgi

    * apt-get install lighttp python-flup
    * move source flask-ims to /var/www
    * grant flask-ims with user www-data  access
       chown -R www-data:www-data 
    * append fcgi.conf to lighttpd.conf
    * restart lighttp services
    * access: http://hostname/ims
    
其他
~~~~~~~~

  * 工具

    * py.sh : 格式化代码
    * sub.sh : 提交代码