from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your secret key' # Change this to a random string
    app.permanent_session_lifetime = 3600 # 1 hour (if the session is not used for 1 hour, it will be deleted)
    app.config['SESSION_COOKIE_SECURE'] = True # The session cookies will only be sent over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True # The session cookies will not be accessible by JavaScript
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .initialpage import initialPage
    from .homepage import homePage
    from .uploading import uploading
    from .additionRepo import additionRepo
    from .repo import repository
    from .invitations import invitations
    from .collaborators import collabPage

    
    app.register_blueprint(initialPage, url_prefix='/')
    app.register_blueprint(homePage, url_prefix='/')
    app.register_blueprint(uploading, url_prefix='/')
    app.register_blueprint(additionRepo, url_prefix='/')
    app.register_blueprint(repository, url_prefix='/repo')
    app.register_blueprint(invitations, url_prefix='/')
    app.register_blueprint(collabPage, url_prefix='/repo')

    return app


    