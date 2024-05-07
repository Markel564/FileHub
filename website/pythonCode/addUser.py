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

        id = g.get_user().id

    
    except:
        # if the user is not authenticated, return False
        return 1


    try:
        # check if the user is already in the session

        if User.query.filter_by(id=id).first() :
            
            user = User.query.filter_by(id=id).first()
            session['user_id'] = id

            if user.githubG != session['token']:
                user.githubG = session['token']
                db.session.commit()
            pass

        else: # if the user is not in the session, we add it
            
            print("User not in session")
            # get the user's information

            # save the user's id in the session
            session['user_id'] = id
            
            user = g.get_user()
            
            name = user.name
            username = user.login
            email = user.email
            avatar = user.avatar_url
            
            print(f"Name is {name}, username is {username}, email is {email} and avatar is {avatar}")
            # add user to database
            new_user = User(id=id, githubG=session['token'], name=name, username=username, email=email, avatarUrl=avatar)
            print("Adding user to the database")
            db.session.add(new_user)
            db.session.commit()
            # load the user's repos to the database
            repos = get_repos()
            
            if not repos:
                print("Error loading projects from GitHub")
                return 3

        g.close()
        print("User added successfully")
        return 0
    
    except SQLAlchemyError as e:
        print(e)
        return 2
    
    except Exception as e:
        print(e)
        return 4