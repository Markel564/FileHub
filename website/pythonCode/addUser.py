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
from .cryptography import generate_key, encrypt_token, decrypt_token
import random
import string
import os
import base64


def add_user(token):
    """
    input: none
    output: True if user has been added to the database, False if not

    This function adds a user to the database
    """


    try:
        
        print ("Adding user to the database")
        # we are going to save the token encrypted in the database
        password = "".join(random.choice(string.ascii_letters) for i in range(16)) # random password
        salt = os.urandom(16) # random salt
        key = generate_key(password, salt)
            
        encrypted_token, iv, tag = encrypt_token(token, key)

        key_to_save = base64.b64encode(key).decode() 
        tag_to_save = base64.b64encode(tag).decode()  
        iv_to_save = base64.b64encode(iv).decode()
        
        session['FileHubKey'] = key_to_save
        session['iv'] = iv_to_save
        session['tag'] = tag_to_save

        

        auth = Auth.Token(token)
        g = Github(auth=auth, base_url="https://api.github.com") 
            
        user = g.get_user()

        name = user.name
        username = user.login
        email = user.email
        avatar = user.avatar_url

        session['user_id'] = user.id

        # add user to database
        user_to_check = User.query.filter_by(id=user.id).first()

        if user_to_check:
            print ("User already in the database")
            # if the user is already in the database, update the token
            user_to_check.githubG = encrypted_token
        else:
            print ("User not in the database")
            new_user = User(id=user.id, githubG=encrypted_token, name=name, username=username, email=email, avatarUrl=avatar)
            db.session.add(new_user)
        db.session.commit()
        print ("User added to the database")

        g.close()

        print ("User added successfully")
        return 0

    except SQLAlchemyError as e:
        print (e)
        return 2
    
    except github.GithubException as e:
        print (e)
        return 5
    
    except Exception as e:
        print (e)
        return 4
    

