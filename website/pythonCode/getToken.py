""" 
This module contains a funcion that gets the token from the session and decrypts it
and therefore authenticates the user
"""
from flask import session
import base64
from .cryptography import decrypt_token
from ..models import User
import os

def get_token():

    """
    input: none
    output: the token or False if the token is not found

    This function gets the token (and other key elements) from the session and decrypts it
    """

    try:
        
        # obtain the FileHubKey (randomly generated previously), iv and tag from the session
        filehub_key_b64 = session.get('FileHubKey')
        iv_b64 = session.get('iv')
        tag_b64 = session.get('tag')
        
        # decode the elements
        filehub_key = base64.b64decode(filehub_key_b64) 
        iv = base64.b64decode(iv_b64)
        tag = base64.b64decode(tag_b64)

        user_id = session.get('user_id')     # get the user id from the session
        user = User.query.filter_by(id=user_id).first() # get the user from the database

        if not user: # if the user is not found, return False
            return False

        token = decrypt_token(user.githubG, filehub_key, iv, tag) # decrypt the token

        return token

    except Exception as e:
        return False



