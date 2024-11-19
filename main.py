from application import create_app
from config import DevelopmentConfig, Config



app = create_app(config_obj=DevelopmentConfig)


with app.app_context():
    from application.seed import create_initial_data
    create_initial_data()


if __name__ == '__main__':
    app.run(
        host=app.config.get("FLASK_RUN_HOST"),
        port=app.config.get("FLASK_RUN_PORT"),
        debug=app.config.get("FLASK_DEBUG")
    )


