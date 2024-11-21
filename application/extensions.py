from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow



db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

ma = Marshmallow()

csrf = CSRFProtect()

bcrypt = Bcrypt()



login_manager.login_view = 'auth.login'
login_manager.login_message = 'You need to login first'
login_manager.login_message_category = ''
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = 'You need to re-login first'
login_manager.needs_refresh_message_category = ''




# flask db init
# flask db migrate -m "<msg>"
# flask db upgrade



