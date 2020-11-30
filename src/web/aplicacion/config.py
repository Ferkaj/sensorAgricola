import os	

secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
PWD = os.path.abspath(os.curdir)	

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/dbase.db'.format(PWD)
SQLALCHEMY_TRACK_MODIFICATIONS = False
 
"""
#Production config
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://konoha:+/2398-FireLeaf@Konoha.mysql.pythonanywhere-services.com/Konoha$default'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_RECYCLE = 280 # For pythonanywhere
"""
