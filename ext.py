from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.contrib.cache import SimpleCache
db = SQLAlchemy()
# Setup the configuration for login manager.
#     1. Set the login page.
#     2. Set the more stronger auth-protection.
#     3. Show the information when you are logging.
#     4. Set the Login Messages type as `information`.
login_manager = LoginManager()
login_manager.login_view = "main.bules.index.views.login"
login_manager.session_protection = "strong"
login_manager.login_message = "请先登陆."  # 默认的闪现消息
login_manager.login_message_category = "info"
@login_manager.user_loader
def load_user(user_id):
    """Load the user's info."""
    from app.models.admin import User
    return User.query.filter_by(id=user_id).first()

simple_cache = SimpleCache()