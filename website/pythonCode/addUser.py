"""
This module contains a function that adds a user to the 
database

"""

from ..models import User
from .. import db
from github import Github, Auth
from flask import session
from sqlalchemy.exc import SQLAlchemyError
from .cryptography import generate_key, encrypt_token, decrypt_token
import random
import string
import os
import base64


def add_user(token: str):
    """
    input: token
    output: 0 if user has been added to the database, other number otherwise

    This function adds a user to the database, as well as a series of session variables,
    such as the key, iv and tag used to encrypt the token. The function also checks if the user
    is already in the database, and if so, updates the token.
    """

    try:
        
        # we are going to save the token encrypted in the database
        password = "".join(random.choice(string.ascii_letters) for i in range(16)) # random password to encrypt the token
        salt = os.urandom(16) # random salt
        key = generate_key(password, salt) # generate the key
        
        # encrypt the token
        encrypted_token, iv, tag = encrypt_token(token, key)

        # save the key, iv and tag in the session in base64 format
        key_to_save = base64.b64encode(key).decode() 
        tag_to_save = base64.b64encode(tag).decode()  
        iv_to_save = base64.b64encode(iv).decode()
        
        session['FileHubKey'] = key_to_save
        session['iv'] = iv_to_save
        session['tag'] = tag_to_save

        
        # authenticate the user
        auth = Auth.Token(token)
        g = Github(auth=auth, base_url="https://api.github.com")  # open a connection to the github api
            
        user = g.get_user() # get the user

        username = user.login 
        avatar = user.avatar_url # we will save the user's avatar since it is will be displayed

        session['user_id'] = user.id # save the user's id in the session

        # add user to database
        user_to_check = User.query.filter_by(id=user.id).first()

        if user_to_check:
            # if the user is already in the database, update the token
            user_to_check.githubG = encrypted_token
        else: 
            # if the user is not in the database, add the user
            new_user = User(id=user.id, githubG=encrypted_token, username=username, avatarUrl=avatar)
            db.session.add(new_user)
        db.session.commit()

        g.close() # close the connection
 
        return 0

    except SQLAlchemyError:
        return 1
    
    except github.GithubException:
        return 2
    
    except Exception:
        return 3
    

