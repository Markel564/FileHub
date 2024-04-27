from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key123'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .initialpage import initialPage
    from .homepage import homePage
    from .uploading import uploading
    from .additionRepo import additionRepo
    from .repo import repository
    from .invitations import invitations
    
    app.register_blueprint(initialPage, url_prefix='/')
    app.register_blueprint(homePage, url_prefix='/')
    app.register_blueprint(uploading, url_prefix='/')
    app.register_blueprint(additionRepo, url_prefix='/')
    app.register_blueprint(repository, url_prefix='/repo')
    app.register_blueprint(invitations, url_prefix='/')


    return app


    