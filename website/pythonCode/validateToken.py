from ..models import User
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
from .getRepos import get_repos
from sqlalchemy.exc import SQLAlchemyError
import requests


def validate_token(token):

    try:
        # authenticate the user

        url = "https://api.github.com/user"

        headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return False
        return True

    except Exception as e:

        return False