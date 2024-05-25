"""
This file contains the functions relevant to loading files
and folders from the user's github account to the database

Basically, a repository or path within a repository is checked
and the files and folders are added to the database

"""

from ..models import Repository, Folder, File
from .. import db
from github import Github
import github
from flask import session
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
import time
from .getHash import sign_file
import os
from sqlalchemy.exc import SQLAlchemyError
import requests
from .getToken import get_token
import shutil


def load_files_and_folders(repoName:str, path=""):

    """
    input:
        - repoName (string): name of the repository
        - path (string): path of the folder within the repository
    output:    
        - 0 if the files and folders were loaded successfully, other number otherwise

    This function loads the files and folders from the repository to the database
    """
    token = get_token() # get the token from the session

    if not token: # if the token is not found, return an error code
        return 6 

    try:

        # authenticate the user
        g = github.Github(token)
        user = g.get_user()

        # obtain the owner of the repo
        # for that, get the list of repositories of the user
        repositories = user.get_repos()
        for repo in repositories:
            if repo.name == repoName:
                owner = repo.owner.login
                break

        # make the API call to get the contents of the repository
        url = f"https://api.github.com/repos/{owner}/{repoName}/contents/{path}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200: # if the request was not successful, return an error code
            return 4
        
        contents = response.json() # get the contents of the repository

        
        files, folders, lastupdates = [], [], [] # lists to store the files, folders and last updated dates
        repository = Repository.query.filter_by(name=repoName).first() # get the repository from the database

        if not repository: # if the repository is not in the database, return an error code
            return 2

        # we are going to check the files and folders in the repository and add them to the database or modify them
        for content_file in contents: 

            if content_file['type'] == "file":  # if the content is a file
                
                # add the file to the database associated with the repository
                # the id of the file is added automatically by the database

                # check if there is a file in that folder with the same name
                file = File.query.filter_by(name=content_file['name'], repository_name=repoName, path=str(repoName+'/'+content_file['path'])).first() 
                
                if not file: # if the file is not in the database, add it
                    # given that there is an issue with last_modified attribute (see https://github.com/PyGithub/PyGithub/issues/629)
                    # we will see the most recent commit of the file and get the last modified date from there
                    last_modified = get_last_modified(content_file['path'], repoName, owner) # get the last modified date of the file
                    
                    # the folder path is the path of the file without the file name
                    folder_path = repoName + '/' + content_file['path'].split(content_file['name'])[0] 

                    file = File(name=content_file['name'], repository_name=repoName, lastUpdated=last_modified, 
                    modified=False, path=str(repoName+'/'+content_file['path']), folderPath=folder_path)
                    db.session.add(file)

                    # also, if the repository is cloned, we have to add the file to the file system

                    if repository.isCloned:
                        # there is a chance that the new file belongs to a folder which we did not have in the database previously
                        directory_path = str(repository.FileSystemPath + repoName + "/" + content_file['path'])
                        directory = os.path.dirname(directory_path)

                        if not os.path.exists(directory): # if the directory does not exist, create it
                            os.makedirs(directory)
                        
                        # and we add the file to the file system
                        download_url = content_file['download_url']

                        if not download_url:
                            return 4

                        response = requests.get(download_url) # make the request to get the file

                        if response.status_code != 200:
                            return 4
                        
                        file_path = str(repository.FileSystemPath + repoName + "/" + content_file['path']) # path of the file in the file system
                        with open(file_path, 'wb') as fileFS:   # open the file and write the content to the path in the fs
                            fileFS.write(response.content)

                        fileFS.close()

                        # sign the file and add the file system path attribute to the file
                        file.FileSystemPath = repository.FileSystemPath + repoName + "/" + content_file['path']
                        file.shaHash = sign_file(file.FileSystemPath)

                        if file.shaHash == None: # this means that the file was not found
                            return 3
                        
                        
                    
                else: # if the file is already in db, check if it has been updated 
                    last_commit_utc = get_last_modified(content_file['path'], repoName, owner)
                    last_commit_str = last_commit_utc.strftime("%Y-%m-%d %H:%M:%S")

                    file_last_updated_utc = file.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
                    if time_difference(last_commit_str, file_last_updated_utc): # if the file has been updated
                        file.lastUpdated = last_commit_utc # update the last updated date of the file
                        # again, if the repository is cloned, we have to add the new version of the file to the file system
                        if repository.isCloned:
                            
                            download_url = content_file['download_url'] # get the download url of the file

                            if not download_url:
                                return 4    
                            
                            response = requests.get(download_url) # make the request to get the file

                            if response.status_code != 200:
                                return 4
                            
                            file_path = str(repository.FileSystemPath + repoName + "/" + content_file['path'])
                            with open(file_path, 'wb') as fileFS:
                                fileFS.write(response.content)
                            
                            fileFS.close()

                            # update the file system path (although this one should be the same) and sign the file
                            file.shaHash = sign_file(repository.FileSystemPath + repoName + "/" + content_file['path'])
                            file.FileSystemPath = repository.FileSystemPath + repoName + "/" + content_file['path']

                            if file.shaHash == None:
                                return 3

                    else: # if the file has not been updated 
                        
                        if repository.isCloned: # if the repository is cloned, check if the file is in the file system
                            file.FileSystemPath = repository.FileSystemPath + repoName + "/" + content_file['path']
                            file.shaHash = sign_file(repository.FileSystemPath + repoName + "/" + content_file['path'])

                            if file.shaHash == None:
                                return 3

                    file.deleted = False # in case it is a file which was set as deleted previously
                db.session.commit()
                lastupdates.append(file.lastUpdated) # add the last updated date of the file to the list
                files.append(content_file['name'])  # add the name of the file to the list
                        
            else:
                
                # add the folder to the database associated with the repository
                folder = Folder.query.filter_by(name=content_file['name'], repository_name=repoName, path=str(repoName+'/'+content_file['path'])).first()
                
                if not folder: # if the folder is not in the database, add it
                    
                    last_modified = get_last_modified(content_file['path'], repoName, owner) # get the last modified date of the folder

                    # the folder path is the path of the folder without the folder name
                    folder_path = repoName + '/' + content_file['path'][0:len(content_file['path'])-len(content_file['name'])]
                    
                    # the folder path is the repoName + the path of the folder without the folder name
                    folder = Folder(name=content_file['name'], repository_name=repoName, 
                    lastUpdated=last_modified, modified=False, path=str(repoName+'/'+ content_file['path']), folderPath=folder_path) 

                    db.session.add(folder)

                    # also, if the repository is cloned, we have to add the folder to the file system

                    if repository.isCloned:
                        # get the directory path of the folder
                        directory_path = str(repository.FileSystemPath + repoName + "/" + content_file['path'])
                        directory = os.path.dirname(directory_path)

                        if not os.path.exists(directory_path): # if the directory does not exist (which it shoudnt as it was not in the database), create it
                            os.makedirs(directory_path)
                        
                        # also, we have to add the filesystem path to the folder
                        folder.FileSystemPath = directory_path
                        # in this case, we will not make a signature of the folder 


                else: # if the folder is already in db, 
                    
                    # check if it has been updated and change modified to True if it has
                    # for this, we will check the files within the folder and see if they have been updated
                    last_commit_utc = get_last_modified(content_file['path'], repoName, owner)
                    last_commit_str = last_commit_utc.strftime("%Y-%m-%d %H:%M:%S")

                    folder_last_updated_utc = folder.lastUpdated.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")

                    if time_difference(last_commit_str, folder_last_updated_utc): # if the folder has been updated
                        folder.lastUpdated = last_commit_utc
                        
                        # update the last updated date of the father folders (folders to which this folder belongs)
                        update_dates(folder.path, repoName, last_commit_utc)

                    if repository.isCloned: # if the repository is cloned, we have to check if the folder is in the file system
                        # there is a chance that the new folder belongs to a folder which we did not have in the database
                        directory_path = str(repository.FileSystemPath + repoName + "/" + content_file['path'])
                        directory = os.path.dirname(directory_path)

                        if not os.path.exists(directory_path): # if the directory does not exist, create it
                            os.makedirs(directory_path)

                        folder.FileSystemPath = directory_path # add the file system path to the folder
                        
                db.session.commit()
                lastupdates.append(folder.lastUpdated) # add the last updated date of the folder to the list
                folders.append(content_file['name']) # add the name of the folder to the list

        # the size of the repo might be empty, but it should return a valid response
        # repo.size is not always accurate (e.g. if the repository is empty, it will not return 0 due to the
        # .git folder). So, we just keep track of the number of files and folders

        if files == [] and folders == []: # if the repository is empty, return 0
            g.close() # close the connection
            return 0 # return 0

        # update the last updated date of the repository
        if repository.lastUpdated < max(lastupdates):
            repository.lastUpdated = max(lastupdates)
            db.session.commit()

        # also, if we are in a folder, we need to update the last updated date of the folder
        if path != "": # if it is not the root directory
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

        # Moreover, there is a chance that a directory in the fs is left empty, and in Git, an empty directory
        # will be deleted. So, we have to check if there are empty directories in the file system and delete them

        # to do this, we can just list the folders obtained from the Git call, and the ones that exist in the file system
        # and delete the ones that are not in the Git call

        # there are 2 solutions depending on whether the repository is cloned or not
        if repository.isCloned:

            # list all the folders in the repo.filesystemPath
            complete_path = os.path.join(repository.FileSystemPath, repoName, path)

            # obtain all folders in the path
            foldersAndFiles = os.listdir(complete_path)
            # Filtrar solo los directorios
            directories = [d for d in foldersAndFiles if os.path.isdir(os.path.join(complete_path, d))]


            # eliminate those that are not in the folders list (except .git folder)
            for directory in directories:
                if directory not in folders and directory != ".git":
                    shutil.rmtree(os.path.join(complete_path, directory))
                    # also, we have to delete the folder from the database
                    if path == "": # if we are in the root directory
                        path_of_folder = str(repoName + '/' + directory)
                    else:
                        path_of_folder = str(repoName + '/' + path + "/" + directory)

                    folder = Folder.query.filter_by(repository_name=repoName, path=path_of_folder).first()

                    subfolders = Folder.query.filter(Folder.folderPath.like(f"{folder.path}/%")).all() # filter the subfolders
                    subfiles = File.query.filter(File.folderPath.like(folder.path + "/%")).all() # filter the files
                    
                    for subfolder in subfolders: # delete the subfolders
                        db.session.delete(subfolder)
          
                    db.session.delete(folder)

                    # also, we have to delete the files within the folder
                    for file in subfiles:
                        db.session.delete(file)
    
                    db.session.commit()
        
        else:
            # if the repository is not cloned, we have to check the folders in the database and compare them with the folders list
            # and delete those that are not in the folders list
            for f in folders:
                path_to_folder = None
                if path == "": # if we are in the root directory
                    path_of_folder = str(repoName + '/' + f)
                else:
                    path_of_folder = str(repoName + '/' + path + "/" + f)
                all_folders = Folder.query.filter_by(repository_name=repoName).all()
                for fol in all_folders:
                    if fol.path == path_of_folder:
                        path_to_folder = fol.path
                        break
                folder = Folder.query.filter_by(repository_name=repoName, path=path_to_folder).first() # get the folder from the database
                folders_in_DB = Folder.query.filter(Folder.folderPath.like(f"{folder.path}/")).all() # filter the subfolders
                for folder in folders_in_DB:
                    if folder.name not in folders:

                        # get the subfolders and files of the folder
                        subfolders = Folder.query.filter(Folder.folderPath.like(f"{folder.path}/%")).all() # filter the subfolders
                        subfiles = File.query.filter(File.folderPath.like(folder.path + "/%")).all() # filter the files

                        for subfolder in subfolders:
                            db.session.delete(subfolder)
                        
                        for file in subfiles:
                            db.session.delete(file)
                        db.session.delete(folder)
                        db.session.commit()

        # finally, we have to delete the files that are deleted from github but remain in the database and file system
        # for that, we will list the files in this path and compare them with the files in the database
        # and delete those that are not in the files list
        if path == "":
            folderPath = repoName
        else:
            folderPath = repoName + "/" + path
        if folderPath[-1] != "/":
            folderPath += "/"
        files_in_db = File.query.filter_by(repository_name=repoName, folderPath=folderPath).all() # get the files in the database

        for file in files_in_db:
            if file.name not in files: # if the file is not in the files list
                db.session.delete(file)
                db.session.commit()
                if repository.isCloned: # if the repository is cloned, we have to delete the file from the file system
                    os.remove(file.FileSystemPath)
        db.session.commit() 
        g.close()

        return 0
        
    except github.GithubException:
        return 4
    
    except SQLAlchemyError:
        return 5
    
    except Exception:
        return 6


def get_files_and_folders(repoName: str, father_dir: str):
    """ 
    input:
        - repoName: name of the repository
        - father_dir: path of the folder where the files and folders are located
    output:
        - files: list of files in the folder, False if there is an error
    returns the files and folders in the folder
    """


    token = get_token() # get the token from the session

    if not token: # if the token is not found, return an error code
        return False, False
    
    files = File.query.filter_by(repository_name=repoName, folderPath=father_dir).all() # get the files in the folder
    folders = Folder.query.filter_by(repository_name=repoName, folderPath=father_dir).all() # get the folders in the folder

    for file in files[:]: # remove the files that are deleted (they will not show up in the representation)
        if file.deleted:
            files.remove(file)

    for folder in folders[:]: # same applies to folders
        if folder.deleted:
            folders.remove(folder)
    
    # we keep the names of the file and folders as well as the last updated date, the modified attribute and the path
    files = [[file.name, file.lastUpdated, file.modified, file.folderPath] for file in files]
    folders = [[folder.name, folder.lastUpdated, folder.modified, folder.folderPath] for folder in folders]
    
    return files, folders


def get_last_modified(path: str, repoName: str, owner: str):
    """ 
    input:
        - path: path of the file
        - repoName: name of the repository
        - owner: owner of the repository
    output:
        - last modified date of the file
    """

    token = get_token() # get the token from the session

    if not token:
        return None # if the token is not found, return None

    url = f"https://api.github.com/repos/{owner}/{repoName}/commits?path={path}" # get the commits of the file
    params = {
        "path": path,
        "per_page": 1 # we only want the last commit
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        
        response = requests.get(url, headers=headers, params=params) # make the request to the API

        if response.status_code != 200: # if the request was not successful
            return None # return None
        
        commit = response.json()[0] # get the last commit of the file
        last_commit = commit['commit']['author']['date'] # get the last commit date
        
        last_commit_datetime = datetime.fromisoformat(last_commit.rstrip('Z')) # convert the string to a datetime object
        gmt = pytz.timezone('GMT') # convert the datetime object to GMT
        last_modified_gmt = gmt.localize(last_commit_datetime) # localize the datetime object

        timezone = get_localzone() # get the local timezone of the user
        last_modified = last_modified_gmt.astimezone(timezone) # convert the previous datetime object to the local timezone

        last_modified = last_modified.replace(tzinfo=None) # remove the timezone information

        return last_modified # return the last modified date


    except Exception:
        return None




def update_dates(father_dir: str, repo_name: str, last_modified: datetime):
    """ 
    This function updates the dates of the folders where the file is located and the repository
    input:
        - father_dir path of the folder where the file is located
        - repo_name: name of the repository
        - last_modified: last modified date of the file
    output: None
    Update the dates of the folders above a given folder and the repository

    """
    repo = Repository.query.filter_by(name=repo_name).first()   # get the repository from the database

    
    while father_dir != repo.name + "/": # while we have not reached the repository
        folder = Folder.query.filter_by(path=father_dir[:-1], repository_name=repo.name).first() # find a folder in the database

        if not folder:  
            pass # it will be added later in the function load_files_and_folders
        
        else:
            folder.lastUpdated = last_modified # just update the date of the folder to now
            folder.modified = True # set modified to True
        
        father_dir = father_dir.rsplit("/",2)[0] + "/" # go to its father directory
    
    repo.lastUpdated = last_modified # update the last updated date of the repository
    db.session.commit()  # commit the changes



def time_difference(time1: str, time2: str):
    """ 
    input:
        - time1: string representing a time
        - time2: string representing a time
    output:
        - True if the difference between the 2 strings is greater than 1 minute, False otherwise
    This function returns True if the difference between the 2 strings is greater than 1 minute
    """ 

    time1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S") # convert the strings to datetime objects
    time2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")  

    difference = abs(time1-time2) # get the difference between the 2 times

    if difference.total_seconds() > 60: # if the difference is greater than 1 minute
        return True  # return True
    return False # return False