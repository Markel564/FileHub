from ..models import User, Repository, File
from .. import db
from flask import session
import os
from sqlalchemy.exc import SQLAlchemyError


def open_file(repoName, path):

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return 1

    repo = Repository.query.filter_by(name=repoName).first()

    if not repo:
        return 2
    
    if not repo.isCloned:
        return 3
    
    file = File.query.filter_by(repository_name=repoName, path=path).first()

    if not file:
        return 4
    
    if not os.path.exists(file.FileSystemPath):
        return 5
    
    try:
        # open file so that the user can see it
        if os.name == 'nt':
            os.system('xdg-open "{}"'.format(file.FileSystemPath))
            return 0
        elif os.name == 'posix':
            os.system('xdg-open "{}"'.format(file.FileSystemPath))
            return 0
        else:
            return 6

    except Exception as e:
        print(e)
        return 7
