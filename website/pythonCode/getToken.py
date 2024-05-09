from flask import session
import base64
from .cryptography import decrypt_token
from ..models import User
import os

def get_token():

    try:

        filehub_key_b64 = session.get('FileHubKey')
        iv_b64 = session.get('iv')
        tag_b64 = session.get('tag')
        
        print (f"filehub_key_b64: {filehub_key_b64}")
        filehub_key = base64.b64decode(filehub_key_b64)
        iv = base64.b64decode(iv_b64)
        tag = base64.b64decode(tag_b64)

        print (f"types: {type(filehub_key)}, {type(iv)}, {type(tag)}")
        user_id = session.get('user_id')    
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return False

        token = decrypt_token(user.githubG, filehub_key, iv, tag)

        return token

    except Exception as e:
        print ("In get token", e)
        return False



