from flask import Flask
from .extensions import db, migrate, login_manager, bcrypt
from config import Config


def create_app(config_obj: Config) -> Flask:
    app = Flask(__name__, template_folder=config_obj.TEMPLATES_FOLDER, static_folder=config_obj.STATIC_FOLDER)

    app.config.from_object(config_obj)

    db.init_app(app)
    migrate.init_app(app, db, directory=config_obj.MIGRATE_FOLDER)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.app_context().push()

    from application.core.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()


    from application.core import core as core_blueprint
    app.register_blueprint(core_blueprint, url_prefix='/')

    from application.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from application.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from application.customers import customer as customer_blueprint
    app.register_blueprint(customer_blueprint, url_prefix='/customers/<int:cust_id>')

    from application.providers import provider as provider_blueprint
    app.register_blueprint(provider_blueprint, url_prefix='/providers/<int:prov_id>')

    from application.apis import api_bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app


