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
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
import time
from cachetools import TTLCache
from .getHash import sign_file
import os
from sqlalchemy.exc import SQLAlchemyError
import requests
from .getToken import get_token
from .cloneRepo import windows_to_unix_path
import time



def load_files_and_folders(repoName, path=""):

    """
    It will be done when the user clicks on a repository for the first time

    It is important to mention that the database will be updated every time the user clicks on the repository,
    and that it stores the files and folders in the / (not recursively)
    """
    token = get_token()

    if not token:
        return 6
    
    
    try:

        # authenticate the user

        g = github.Github(token)
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
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers)
        print (url)
        if response.status_code != 200:
            return 4
        
        contents = response.json()

        
        files, folders, lastupdates = [], [], []
        repository = Repository.query.filter_by(name=repoName).first()

        if not repository:
            return 2

        start = time.time()
        for content_file in contents:

            if content_file['type'] == "file":
                

                # add the file to the database associated with the repository

                # the id of the file is added automatically by the database
                # check if there is a file in that folder with the same name
    
                file = File.query.filter_by(name=content_file['name'], repository_name=repoName, path=str(repoName+'/'+content_file['path'])).first() 
                
                if not file: # if the file is not in the database, add it
                    # given that there is an issue with last_modified attribute (see https://github.com/PyGithub/PyGithub/issues/629)
                    # we will see the most recent commit of the file and get the last modified date from there
                    
                    last_modified = get_last_modified(content_file['path'], repoName, owner)
                    
                    # the folder path is the path of the file without the file name
                    folder_path = repoName + '/' + content_file['path'].split(content_file['name'])[0] 

                    
                    file = File(name=content_file['name'], repository_name=repoName, lastUpdated=last_modified, 
                    modified=False, path=str(repoName+'/'+content_file['path']), folderPath=folder_path)

                    db.session.add(file)

                    # also, if the repository is cloned, we have to add the file to the file system

                    if repository.isCloned:
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
                    
                    last_commit_utc = get_last_modified(content_file['path'], repoName, owner)
                    last_commit_str = last_commit_utc.strftime("%Y-%m-%d %H:%M:%S")

                    file_last_updated_utc = file.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")

                    if time_difference(last_commit_str, file_last_updated_utc): # if the file has been updated
                        # file.modified = True
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

                        if repository.isCloned:
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
                    
                    last_modified = get_last_modified(content_file['path'], repoName, owner)

                    # the folder path is the path of the folder without the folder name
                
                    folder_path = repoName + '/' + content_file['path'][0:len(content_file['path'])-len(content_file['name'])]
                    
                    # the folder path is the repoName + the path of the folder without the folder name
                    

                    folder = Folder(name=content_file['name'], repository_name=repoName, 
                    lastUpdated=last_modified, modified=True, path=str(repoName+'/'+ content_file['path']), folderPath=folder_path) 

                    db.session.add(folder)
                    # the last updated date of the repository will be the last updated date of the file

                else: # if the folder is already in db, 
                    
                    # check if it has been updated and change modified to True if it has
                    # for this, we will check the files within the folder and see if they have been updated

                    last_commit_utc = get_last_modified(content_file['path'], repoName, owner)
                    last_commit_str = last_commit_utc.strftime("%Y-%m-%d %H:%M:%S")

                    folder_last_updated_utc = folder.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")

                    if time_difference(last_commit_str, folder_last_updated_utc):
                        # folder.modified = True
                        folder.lastUpdated = last_commit_utc
                        
                        # update the last updated date of the files within the folder
                        update_dates(folder.path, repoName, last_commit_utc)

                        # if repository.isCloned:
                        #     folder.modified = False

                    else:
                        # folder.modified = False
                        pass
                        
                db.session.commit()
                lastupdates.append(folder.lastUpdated)
                folders.append(content_file['name'])

        # the size of the repo might be empty, but it should return a valid response
        # repo.size does not work always as the cache might be empty and it takes time to update


        if files == [] and folders == []: # if the repository is empty

            g.close() # close the connection
            return 0 # return 0

        # update the last updated date of the repository
        if repository.lastUpdated < max(lastupdates):
            repository.lastUpdated = max(lastupdates)

        # moreover, we have to eliminate the files and folders that are not in the repository anymore
        # we will do this by checking the files and folders in the database and see if they are in the files and folders list
        # if they are not, we will delete them
        files_db = File.query.filter_by(repository_name=repoName).all()
        folders_db = Folder.query.filter_by(repository_name=repoName).all()

        for file in files_db:
            if file.name not in files:
                db.session.delete(file)
                db.session.commit()

                # if the repository is cloned, we have to delete the file from the file system
                if repository.isCloned:
                    os.remove(file.FileSystemPath)
            
        for folder in folders_db:
            if folder.name not in folders:
                db.session.delete(folder)
                db.session.commit()

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
                    
                    folder.modified = False # if the folder has not been updated, we set modified to False

        db.session.commit()

        # finally, there is a chance that a directory is left empty, so we will delete it
        if repository.isCloned:
            # list all the folders in the repo.filesystemPath
            complete_path = os.path.join(repository.FileSystemPath, repoName, path)

            # obtain all folders in the path
            foldersAndFiles = os.listdir(complete_path)
            # Filtrar solo los directorios
            directories = [d for d in foldersAndFiles if os.path.isdir(os.path.join(complete_path, d))]
            print("Directories", directories)
            # eliminate the empty ones
            for directory in directories:
                files = os.listdir(os.path.join(complete_path, directory))
                print ("Files", files)
                if files == []:
                    # remove from the file system the empty directory
                    print ("Removing directory", os.path.join(complete_path, directory))
                    os.rmdir(os.path.join(complete_path, directory))
    

        g.close()

        return 0
        
    except github.GithubException as e:
        print (e)
        return 4
    
    except SQLAlchemyError as e:
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


def get_last_modified(path, repoName, owner):

    token = get_token()

    if not token:
        return None

    url = f"https://api.github.com/repos/{owner}/{repoName}/commits?path={path}"
    params = {
        "path": path,
        "per_page": 1 # we only want the last commit
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        
        now = time.time()
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

        return last_modified


    except Exception as e:
        return None





def update_dates(father_dir, repo_name, last_modified):
    """ 
    This function updates the dates of the folders where the file is located and the repository
    input:
        - father_dir (string): path of the folder where the file is located
        - repo_name (string): name of the repository
    output: None

    """
    repo = Repository.query.filter_by(name=repo_name).first()  

    
    while father_dir != repo.name + "/": # while we have not reached the repository
        folder = Folder.query.filter_by(path=father_dir[:-1], repository_name=repo.name).first() # find the folder in the database

        if not folder:  
            pass # it will be added later in the function load_files_and_folders
        
        else:
            folder.lastUpdated = last_modified # just update the date of the folder to now
            folder.modified = True
        
        father_dir = father_dir.rsplit("/",2)[0] + "/" # go to its father directory
    
    repo.lastUpdated = last_modified # update the last updated date of the repository
    db.session.commit() 



def time_difference(time1: str, time2: str):
    """ 
    input:
        - time1: string representing a time
        - time2: string representing a time
    output:
        - True if the difference between the 2 strings is greater than 1 minute, False otherwise
    This function returns True if the difference between the 2 strings is greater than 1 minute
    """ 

    time1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
    time2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")

    difference = abs(time1-time2)

    if difference.total_seconds() > 60:
        return True
    return False