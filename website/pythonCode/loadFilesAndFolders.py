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
import time
from cachetools import TTLCache
from .getHash import sign_file
import os
from sqlalchemy.exc import SQLAlchemyError
import requests


# Define a cache with a time-to-live (TTL) of 1 hour
cache = TTLCache(maxsize=1000, ttl=3600)


def load_files_and_folders(repoName, path=""):

    """
    It will be done when the user clicks on a repository for the first time

    It is important to mention that the database will be updated every time the user clicks on the repository,
    and that it stores the files and folders in the / (not recursively)
    """
    user_id = session.get('user_id')
    userDB = User.query.filter_by(id=user_id).first()

    # if the user is not in the database, return False
    if not userDB:
        return 1
    
    
    try:

        # authenticate the user

        g = github.Github(userDB.githubG)
        user = g.get_user()

        # obtain the owner of the repo
        # get the list of repositories of the user
        repositories = user.get_repos()
        for repo in repositories:
            if repo.name == repoName:
                owner = repo.owner.login
                break

        # make the API call
        url = f"https://api.github.com/repos/{owner}/{repoName}/contents/{path}"
        headers = {
            "Authorization": f"token {userDB.githubG}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return 4
        
        contents = response.json()

        
        files, folders, lastupdates = [], [], []

        repository = Repository.query.filter_by(name=repoName).first()

        if not repository:
            return 2

        for content_file in contents:

            if content_file['type'] == "file":
                

                # add the file to the database associated with the repository

                # the id of the file is added automatically by the database
                # check if there is a file in that folder with the same name
    
                file = File.query.filter_by(name=content_file['name'], repository_name=repoName, path=str(repoName+'/'+content_file['path'])).first() 
                
                if not file: # if the file is not in the database, add it
                    # given that there is an issue with last_modified attribute (see https://github.com/PyGithub/PyGithub/issues/629)
                    # we will see the most recent commit of the file and get the last modified date from there

                    print (f"File {content_file['name']} not in db")
                    last_modified = get_last_modified(content_file['path'], repoName, owner, userDB.githubG)
                    
                    # the folder path is the path of the file without the file name
                    folder_path = repoName + '/' + content_file['path'].split(content_file['name'])[0]

                    file = File(name=content_file['name'], repository_name=repoName, lastUpdated=last_modified, 
                    modified=False, path=str(repoName+'/'+content_file['path']), folderPath=folder_path)

                    print (f"Created file with file.path: {file.path} and file.folderPath: {file.folderPath} with last updated date {file.lastUpdated}")

                    db.session.add(file)


                    # also, if the repository is cloned, we have to add the file to the file system

                    if repository.isCloned:
                        print ("REPO CLONED")
                        # there is a chance that the new file belongs to a folder which we did not have in the database
                        directory_path = str(repository.FileSystemPath + repoName + "/" + content_file['path'])
                        directory = os.path.dirname(directory_path)

                        if not os.path.exists(directory): # if the directory does not exist, create it
                            os.makedirs(directory)
                        
                        # and we add the file to the file system
                        download_url = content_file['download_url']

                        if not download_url:
                            return 4

                        response = requests.get(download_url)

                        if response.status_code != 200:
                            return 4
                        
                        file_path = str(repository.FileSystemPath + repoName + "/" + content_file['path'])
                        with open(file_path, 'wb') as fileFS:
                            fileFS.write(response.content)


                        fileFS.close()

                        # sign the file and add the file system path
                        file.FileSystemPath = repository.FileSystemPath + repoName + "/" + content_file['path']
                        file.shaHash = sign_file(file.FileSystemPath)

                        if file.shaHash == None:
                            return 3
                        
                        
                    
                else: # if the file is already in db, check if it has been updated and change modified to True if it has
                    
                    print (f"File {content_file['name']} in db")
                    last_commit_utc = get_last_modified(content_file['path'], repoName, owner, userDB.githubG)
                    last_commit_str = last_commit_utc.strftime("%Y-%m-%d %H:%M:%S")

                    file_last_updated_utc = file.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")

                    print (f"Last commit: {last_commit_str} and last updated: {file_last_updated_utc}")
                    if file_last_updated_utc != last_commit_str: # if the file has been updated
                        file.modified = True
                        file.lastUpdated = last_commit_utc

                        # again, if the repository is cloned, we have to add the file to the file system
                        if repository.isCloned:

                            download_url = content_file['download_url']

                            if not download_url:
                                return 4    
                            
                            response = requests.get(download_url)

                            if response.status_code != 200:
                                return 4
                            
                            file_path = str(repository.FileSystemPath + repoName + "/" + content_file['path'])

                            with open(file_path, 'wb') as fileFS:
                                fileFS.write(response.content)
                            
                            fileFS.close()


                            file.shaHash = sign_file(repository.FileSystemPath + repoName + "/" + content_file['path'])
                            file.FileSystemPath = repository.FileSystemPath + repoName + "/" + content_file['path']

                            if file.shaHash == None:
                                return 3

                    
                    else: # if the file has not been updated
                        file.modified = False

                        if repository.isCloned:
                            file.modified = False

                            file.FileSystemPath = repository.FileSystemPath + repoName + "/" + content_file['path']
                            file.shaHash = sign_file(repository.FileSystemPath + repoName + "/" + content_file['path'])

                            if file.shaHash == None:
                                return 3

                db.session.commit()
                lastupdates.append(file.lastUpdated)
                files.append(content_file['name'])

                        
            else:
                
    
                # add the folder to the database associated with the repository

                # before adding the folder, check if it is already in the database (in the same directory)

                folder = Folder.query.filter_by(name=content_file['name'], repository_name=repoName, path=str(repoName+'/'+content_file['path'])).first()

                
                if not folder: # if the folder is not in the database, add it
                    
                    last_modified = get_last_modified(content_file['path'], repoName, owner, userDB.githubG)

                    # the folder path is the path of the folder without the folder name
                
                    folder_path = repoName + '/' + content_file['path'][0:len(content_file['path'])-len(content_file['name'])]
                    
                    # the folder path is the repoName + the path of the folder without the folder name
                    

                    folder = Folder(name=content_file['name'], repository_name=repoName, 
                    lastUpdated=last_modified, modified=False, path=str(repoName+'/'+ content_file['path']), folderPath=folder_path) 

                    print (f"Created folder with folder.path: {folder.path} and folder.folderPath: {folder.folderPath}")
                    db.session.add(folder)
                    # the last updated date of the repository will be the last updated date of the file
                

                else: # if the folder is already in db, check if it has been updated and change modified to True if it has
                    
                    last_commit_utc = get_last_modified(content_file['path'], repoName, owner, userDB.githubG)
                    last_commit_str = last_commit_utc.strftime("%Y-%m-%d %H:%M:%S")

                    folder_last_updated_utc = folder.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")

                    if folder_last_updated_utc != last_commit_str:
                        folder.modified = True
                        folder.lastUpdated = last_commit_utc
                        
                        if repository.isCloned:
                            folder.modified = False

                    else:
                        folder.modified = False
                        
                db.session.commit()
                lastupdates.append(folder.lastUpdated)
                folders.append(content_file['name'])


        # the size of the repo might be empty, but it should return a valid response
        # repo.size does not work always as the cache might be empty and it takes time to update


        if files == [] and folders == []: # if the repository is empty

            # clear the files and folders in the database of that path
            files_in_db = File.query.filter_by(repository_name=repoName, folderPath=repoName + '/' + path).all()
            folders_in_db = Folder.query.filter_by(repository_name=repoName, folderPath=repoName + '/' + path).all()

            for file in files_in_db:
                db.session.delete(file)
            
            for folder in folders_in_db:
                db.session.delete(folder)
            
            last_updated = get_last_modified(path, repoName, owner, userDB.githubG)
            repository.lastUpdated = last_updated
            db.session.commit()

            g.close()
            return 0

        # update the last updated date of the repository
        if repository.lastUpdated < max(lastupdates):
            repository.lastUpdated = max(lastupdates)


        # also, if we are in a folder, we need to update the last updated date of the folder
        if path != "":
            folder = Folder.query.filter_by(name=path.split('/')[-1], repository_name=repoName, path=str(repoName + '/'+ path)).first()
            if folder:
                last_updated = repository.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
                folder_last_updated = folder.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
                if last_updated != folder_last_updated:
                    folder.modified = True # if the folder has been updated, we set modified to True
                    folder.lastUpdated = repository.lastUpdated # update the last updated date of the folder to the one calculated before
                else:
                    
                    folder.modified = False
                


        # eliminate the files and folders that are not in the github repository
        files_in_db = File.query.filter_by(repository_name=repoName, folderPath=repoName + '/' + content_file['path'].split(content_file['name'])[0]).all()
        folders_in_db = Folder.query.filter_by(repository_name=repoName, folderPath=repoName + '/' + content_file['path'].split(content_file['name'])[0]).all()


        if len(files_in_db) > len(files):
            for file in files_in_db:
                if file.name not in files:
                    db.session.delete(file)
        
        if len(folders_in_db) > len(folders):
            for folder in folders_in_db:
                if folder.name not in folders:
                    db.session.delete(folder)

        
        db.session.commit()

        g.close()

        return 0
        
    except github.GithubException as e: 
        print (e)
        return 4
    
    except SQLAlchemyError:
        return 5
    
    except Exception as e:
        print (e)
        return 6



def get_files_and_folders(repoName, father_dir):

    # get the files and folders from the database
    user_id = session.get('user_id')

    if not user_id:
        return False, False
    
    files = File.query.filter_by(repository_name=repoName, folderPath=father_dir).all()
    folders = Folder.query.filter_by(repository_name=repoName, folderPath=father_dir).all()
    
    for file in files[:]:
        if file.deleted:
            files.remove(file)

    for folder in folders[:]:
        if folder.deleted:
            folders.remove(folder)
    
    # we keep the names of the file and folders as well as the last updated date
    files = [[file.name, file.lastUpdated, file.modified, file.folderPath] for file in files]
    folders = [[folder.name, folder.lastUpdated, folder.modified, folder.folderPath] for folder in folders]
    
    return files, folders


def get_last_modified(path, repoName, owner, token):

    url = f"https://api.github.com/repos/{owner}/{repoName}/commits?path={path}"

    params = {
        "path": path,
        "per_page": 1 # we only want the last commit
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }


    cached_last_modified = cache.get(path)
    if cached_last_modified:
        return cached_last_modified

    try:
        
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return None
        
        commit = response.json()[0]
        last_commit = commit['commit']['author']['date']

        
        last_commit_datetime = datetime.fromisoformat(last_commit.rstrip('Z'))
        gmt = pytz.timezone('GMT')
        last_modified_gmt = gmt.localize(last_commit_datetime)

        timezone = get_localzone()
        last_modified = last_modified_gmt.astimezone(timezone)

        last_modified = last_modified.replace(tzinfo=None)
        cache[path] = last_modified # store the last modified date in the cache

        return last_modified


    except Exception as e:
        print (e)
        return None



