from ..models import User, Repository, Folder, File
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session


def get_files_and_folders(repoName):

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    # if the user is not in the database, return False
    if not user:
        return False

    
    try:

        # authenticate the user
        g = github.Github(user.g)
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
                file = file = File(name=content_file.name, repository_name=repoName, user_id=user_id, folder_name=None, last_updated=content_file.last_modified)
                db.session.add(file)


            else:
                folders.append(content_file.name)

                # add the folder to the database associated with the repository
                folder = Folder(name=content_file.name, repository_name=repoName, user_id=user_id, last_updated=content_file.last_modified)
                db.session.add(folder)

        db.session.commit()

        folders_in_repo = folders 

        # add the contents of the folders to the database un until there are no more folders to add
        while folders_in_repo:
            
            for folder in folders_in_repo:

                ack = add_contents(folder, repoName, user_id, user)



        return files, folders
        
    
    except github.GithubException as e:
        return False


def add_contents(folderName, repoName, user_id, user):

    user = User.query.filter_by(id=user_id).first()

    # if the user is not in the database, return False
    if not user:
        return False
    
    try:

    # see the contents of the folder

        repo = user.get_repo(repoName)
        contents = repo.get_contents(folderName)

        files = []
        folders = []

        for content_file in contents:

            if content_file.type == "file":
                files.append(content_file.name)

                # add the file to the database associated with the repository
                file = file = File(name=content_file.name, repository_name=repoName, user_id=user_id, folder_name=folderName, last_updated=content_file.last_modified)
                db.session.add(file)

            else:
                folders.append(content_file.name)

                # add the folder to the database associated with the repository
                folder = Folder(name=content_file.name, repository_name=repoName, user_id=user_id, last_updated=content_file.last_modified)
                db.session.add(folder)
    
    except:
        pass