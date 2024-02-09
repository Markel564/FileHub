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
import pytz
from tzlocal import get_localzone

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
      
        files, folders, lastupdates = [], [], []

        for content_file in contents:
            
            if content_file.type == "file":
                

                # add the file to the database associated with the repository

                # the id of the file is added automatically by the database
                # check if there is a file in that folder with the same name

                file = File.query.filter_by(name=content_file.name, repository_name=repoName).first()

                if not file: # if the file is not in the database, add it

                    # given that there is an issue with last_modified attribute (see https://github.com/PyGithub/PyGithub/issues/629)
                    # we will see the most recent commit of the file and get the last modified date from there

                    commits = repo.get_commits(path=content_file.path)
                    last_commit = commits[0].commit.author.date
                    

                    last_commit = last_commit.replace(tzinfo=None)   
                    # convert it to own timezone
                    gmt = pytz.timezone('GMT')
                    last_modified_gmt = gmt.localize(last_commit)
                    timezone = get_localzone()
                    last_modified = last_modified_gmt.astimezone(timezone)
                    print ("LM2 -->", last_modified)
                    file = File(name=content_file.name, sha=content_file.sha ,repository_name=repoName, lastUpdated=last_modified)
                    print ("file added -->", file.name, file.lastUpdated)
                    db.session.add(file)

                    # the last updated date of the repository will be the last updated date of the file
                    repository = Repository.query.filter_by(name=repoName).first()
                    repository.lastUpdated = last_modified

                files.append(content_file.name)
            else:
                
                
                # add the folder to the database associated with the repository

                # before adding the folder, check if it is already in the database (in the same directory)
                folder = Folder.query.filter_by(name=content_file.name, repository_name=repoName).first()

                if not folder: # if the folder is not in the database, add it

                    commits = repo.get_commits(path=content_file.path)
                    last_commit = commits[0].commit.author.date
                    

                    
                    last_commit = last_commit.replace(tzinfo=None)   
                    # convert it to own timezone
                    gmt = pytz.timezone('GMT')
                    last_modified_gmt = gmt.localize(last_commit)
                    timezone = get_localzone()
                    last_modified = last_modified_gmt.astimezone(timezone)
                    
                    folder = Folder(name=content_file.name, sha=content_file.sha, repository_name=repoName, lastUpdated=last_modified)
                    db.session.add(folder)

                    # the last updated date of the repository will be the last updated date of the file
                    repository = Repository.query.filter_by(name=repoName).first()
                    repository.lastUpdated = last_modified
                
                folders.append(content_file.name)

        # change the last updated for a repository to the last modified date any file/folder
        
    


        # eliminate the files and folders that are not in the github repository
        files_in_db = File.query.filter_by(repository_name=repoName).all()
        folders_in_db = Folder.query.filter_by(repository_name=repoName).all()

        if len(files_in_db) > len(files):
            for file in files_in_db:
                if file.name not in files:
                    db.session.delete(file)
                    print ("file deleted -->", file.name)
        
        if len(folders_in_db) > len(folders):
            for folder in folders_in_db:
                if folder.name not in folders:
                    db.session.delete(folder)
                    print ("folder deleted -->", folder.name)
        db.session.commit()

        g.close()

        return True
        
    
    except github.GithubException as e:
        print (e)
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
    
    # we keep the names of the file and folders as well as the last updated date
    files = [[file.name, file.lastUpdated] for file in files]
    folders = [[folder.name, folder.lastUpdated] for folder in folders]


    
    return files, folders

