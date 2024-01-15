import yaml
from github import Github
from website import create_app, DB_NAME, db
from os import path


def main():
    
    app = create_app()
    with app.app_context():
            if not path.exists('../instance/' + DB_NAME):
                db.create_all()
                print('Created database!')
    app.run(debug=True)

if __name__ == "__main__":
    main()
    
    



