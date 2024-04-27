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


    try:

        auth = Auth.Token(session['token'])
        g = Github(auth=auth, base_url="https://api.github.com")

    except:
        # if the user is not authenticated, return False
        return 1


    try:
        
        identifier = session.get('user_id')


        if User.query.filter_by(id=identifier).first():

            print("User already in session")
            pass

        else: # if the user is not in the session, we add it

            # get the user's information
            id = g.get_user().id
            # save the user's id in the session
            session['user_id'] = id
            
            user = g.get_user()
            
            name = user.name
            username = user.login
            email = user.email
            avatar = user.avatar_url
            
            # add user to database
            new_user = User(id=id, githubG=session['token'], name=name, username=username, email=email, avatarUrl=avatar)

            db.session.add(new_user)
            db.session.commit()
            # load the user's repos to the database
            repos = get_repos()

            if not repos:
                return 3

        g.close()
        return 0
    
    except SQLAlchemyError:
        return 2
    
    except Exception as e:
        print(e)
        return 4