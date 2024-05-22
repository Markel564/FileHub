from github import Github
from website import create_app, DB_NAME, db
from os import path
from flask_login import LoginManager
from website.models import User
from flask_sqlalchemy import session

def main():
    
    app = create_app()

    login_manager = LoginManager()
    login_manager.login_view = 'initialPage.create_token'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, id)
    
    with app.app_context():
            if not path.exists('../instance/' + DB_NAME):
                db.create_all()
                print('Created database!')
    app.run(debug=True)

    
if __name__ == "__main__":
    main()
    
    



