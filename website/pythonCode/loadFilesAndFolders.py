"""
This file contains the functions relevant to loading files
and folders from the user's github account to the database


"""

from ..models import User, Repository, Folder, File
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
from datetime import datetime

def load_files_and_folders(repoName):

    """
    It will be done when the user clicks on a repository for the first time

    It is important to mention that the database will be updated every time the user clicks on the repository,
    and that it stores the files and folders in the / (not recursively)
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    # if the user is not in the database, return False
    if not user:
        return False
    
    try:

        # authenticate the user
        g = github.Github(user.githubG)
        user = g.get_user()

        # get the repo
        repo = user.get_repo(repoName)

        # get the contents of the repo

        contents = repo.get_contents("")

        files = []
        folders = []

        for content_file in contents:
            if content_file.type == "file":
                files.append(content_file.name)

                # add the file to the database associated with the repository

                # the id of the file is added automatically by the database
                file = File(name=content_file.name, sha=content_file.sha ,repository_name=repoName, lastUpdated=datetime.strptime(content_file.last_modified, '%a, %d %b %Y %H:%M:%S %Z'))
                db.session.add(file)


            else:
                folders.append(content_file.name)

                # add the folder to the database associated with the repository
                folder = Folder(name=content_file.name, sha=content_file.sha, repository_name=repoName, lastUpdated=datetime.strptime(content_file.last_modified, '%a, %d %b %Y %H:%M:%S %Z'))
                db.session.add(folder)

        db.session.commit()

        g.close()

        return True
        
    
    except github.GithubException as e:
        return False



def get_files_and_folders(repoName, father_dir=None):

    # get the files and folders from the database
    user_id = session.get('user_id')

    if father_dir:
        files = File.query.filter_by(repository_name=repoName, folder_id=father_dir).all()
        folders = Folder.query.filter_by(repository_name=repoName, fatherFolder_id=father_dir).all()
    else:
        files = File.query.filter_by(repository_name=repoName, folder_id=None).all()
        folders = Folder.query.filter_by(repository_name=repoName, fatherFolder_id=None).all()
    
    # we keep the names of the files and folders
    files = [file.name for file in files]
    folders = [folder.name for folder in folders]
    return files, folders

