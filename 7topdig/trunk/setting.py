import os
# configuration

# root
ROOT = os.path.abspath(os.path.dirname(__file__))

# debug
DEBUG = True

SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

CSRF_ENABLED  = True

# database
DB = r'/db/app.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + ROOT + DB
SQLALCHEMY_NATIVE_UNICODE = None

# admin
ADMINS = ['webadmin@7topdig.com', 'simon.yang.sh@gmail.com']
MAIL_ENABLE = True
ADMIN_MAIL = 'webadmin@7topdig.com'


# debug tool bar
DEBUG_TB_INTERCEPT_REDIRECTS = False

#RECAPTCHA
RECAPTCHA_PUBLIC_KEY  = "6LeNxtQSAAAAAGarvgDEQ-NX7dJTyKaRLDAZYaV7"
RECAPTCHA_PRIVATE_KEY  = "6LeNxtQSAAAAABRsqcTHbtHH0FKcfWYag1I-Zoz_"

# uploads
UPLOADS_DEFAULT_DEST = ROOT + '/app/static/uploads'

AVATAR_PATH = ROOT + '/app/static/avatar'

# douban
DOUBAN_API_PATH = 'http://api.douban.com/book/subject/'
DOUBAN_BOOK_PATH = 'http://book.douban.com/subject/'
