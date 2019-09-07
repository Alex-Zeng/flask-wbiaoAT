class Config(object):
    """Base config class."""
    pass


class ProdConfig(Config):
    """Production config class."""
    DEBUG = False

    # Session key
    SECURE_KEY = 'jiami'

    # MySQL connection  mysql://username:password@server/db
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://jzdcadm:Jzdc@192.168.3.135:3306/Jzdcprd_test2'


class DevConfig(Config):
    """Development config class."""
    # Open the DEBUG
    DEBUG = True
    PORT = 5001
    CACHE_TYPE = 'simple'

    # Session key
    SECRET_KEY = '123456'
    TOKEN_LIFETIME = 60 * 60 * 24

    # mysql数据库连接信息
    uname = 'wbiaotest'
    pwd = 'wbiao1234'
    db_name = 'wbiao_flask'
    db_address = '127.0.0.1'
    db_port = '3306'

    # MySQL connection  mysql://username:password@server/db
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{uname}:{pwd}@{db_address}:{db_port}/{db_name}?charset=utf8'.format(
        uname=uname,
        pwd=pwd,
        db_name=db_name,
        db_address=db_address,
        db_port=db_port)

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True