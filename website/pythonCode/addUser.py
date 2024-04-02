"""
This module contains a function that adds a user to the 
database

"""

from ..models import User
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
from .getRepos import get_repos
from sqlalchemy.exc import SQLAlchemyError



def add_user():
    """
    input: none
    output: True if user has been added to the database, False if not

    This function adds a user to the database
    """

    # get the api token from the config file
    with open("config.yml", 'r') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)

    try:
        # authenticate the user
        auth = Auth.Token(conf['api_token'])
        g = Github(auth=auth, base_url="https://api.github.com")

    except:
        # if the user is not authenticated, return False
        return 1


    try:
    
        # get the user's information
        id = g.get_user().id
        # save the user's id in the session
        session['user_id'] = id
        # get the user's information
        user = g.get_user()
        
        name = user.name
        username = user.login
        email = user.email
        avatar = user.avatar_url

        
        # if user is not in the database (first time loading website), we add it
        if not User.query.filter_by(id=id).first():
            
            print (f"Creating account for {name}")
            # add user to database
            new_user = User(id=id, githubG=conf['api_token'], name=name, username=username, email=email, avatarUrl=avatar)
            db.session.add(new_user)
            db.session.commit()
            # load the user's repos to the database
            repos = get_repos()

            if not repos:
                return 3


        print (f"Authenticated as {user.login}")

        g.close()
        return 0
    
    except SQLAlchemyError:
        return 2
    
    except:
        return 4


