from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bibek'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.sqlite3'
    db = SQLAlchemy()
    db.init_app(app)

    from .models import User
    from .views import views

    app.register_blueprint(views)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'views.index'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
