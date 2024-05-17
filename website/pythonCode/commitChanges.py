""" 
Thus module contains the function that commits the changes made by the user to the Github repository.
""" 
from ..models import User, Repository, File, Folder
from .. import db
from github import Github, Auth
import github
import requests
from flask import session
import os
from sqlalchemy.exc import SQLAlchemyError
import base64
from .getToken import get_token
from datetime import datetime




def commit_changes(repoName: str):
    """ 
    input:
        - repoName: name of repository
        - folderpath: path to the folder in the local file system
    output:
        - 0 if successful, other integer otherwise
    """
    token = get_token() # obtain the token

    if not token: # if the token does not exist, return error
        return False
    
    repoDB = Repository.query.filter_by(name=repoName).first() # filter the repository

    if not repoDB: # if there is not repository, return error
        return 2
    
    if not repoDB.isCloned: # same if the repository is not cloned
        return 3
    
    try:
        
        g = github.Github(token) # create the Github object
        user = g.get_user()

        repositories = user.get_repos() # obtain the repositories of the user, since it is necessary to obtain the owner of the repository

        for repo in repositories:

            if repo.name == repoName:
                owner = repo.owner.login # obtain the owner of the repository
                break

        base_url = f"https://api.github.com/repos/{owner}/{repoName}"

        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }


        for file in repoDB.repository_files: # iterate over the files of the repository
            # path to pass corresponds to the path of the file relative to the repository. It is needed 
            # for commiting the changes to the correct file in Github
            paths = file.folderPath.split('/')[1:]  # split the path to the file in the local file system. This basically removes the first element, 
                                                           # which is the name of the repository

            if paths[0] == '': # if it is empty, it means that the file is in the root of the repository
                path_to_pass = file.name # therefore the it is the name of the file
                inRoot = True # flag to know if the file is in the root of the repository (for later use)
            else:
                inRoot = False
                path_to_pass = ""   
                for elem in paths:
                    path_to_pass += f"{elem}/" # add the path of each folder to the path

                path_to_pass = path_to_pass[:-1] # remove the last '/'
                path_to_pass += f"{file.name}" # add the name of the file to the path

            # file_path is the url to the file in GitHub
            file_path = f"{base_url}/contents/{path_to_pass}" # path to the particular file in Github
                
            # if the user deleted the file (from the local file system), eliminate it from Github
            if file.deleted:
                if not file.addedFirstTime: # if the file was not added for the first time, we can delete it from github (if it is, it is not in github yet, so we can't delete it)

                    response = requests.get(file_path, headers=headers) # make a request to the file in Github
                    if response.status_code != 200:
                        return 5
                    
                    file_data = response.json() # obtain the response in json format

                    # obtain the fields required
                    sha = file_data['sha']

                    # delete from github
                    payload_delete = {
                        'message': f'Deleted file {file.name}',
                        'sha': sha
                    }

                    requests.delete(file_path, headers=headers, json=payload_delete) 

                    # delete from the database 
                    db.session.delete(file)
                    repoDB.lastUpdated = datetime.now() # update the repositories' last update date
                    db.session.commit()

                # to eliminate it from the file system
                if os.path.exists(file.FileSystemPath):
                    os.remove(file.FileSystemPath)
                
                

            # if the user created a file for the first time, upload it to Github
            elif file.addedFirstTime:

                with open(file.FileSystemPath, 'rb') as file_content:
                    content = file_content.read() # read the content of the file
                
                encoded_content = base64.b64encode(content).decode('utf-8') # change the content to base64 as binary files are not allowed in a http json request

                payload_create = {
                    'message': f'Uploaded file {file.name}',
                    'content': encoded_content
                }

                requests.put(file_path, headers=headers, json=payload_create) # make a request to Github to upload the file
                file.addedFirstTime = False # change the status of the file, as it is now in Github
                file.modified = False # no longer modified, for representation purposes
                file.lastUpdated = datetime.now() # update the date of the file
                repoDB.lastUpdated = datetime.now() # update the date of the repository
                db.session.commit() 

    
            # if the user modified a file
            elif file.modified:  

                response = requests.get(file_path, headers=headers) # make a request to the file in Github
                if response.status_code != 200:
                    return 5
                
                file_data = response.json()
                # obtain the fields required (sha)
                sha = file_data['sha']

                with open(file.FileSystemPath, 'rb') as file_content:
                    content = file_content.read() # read the content of the file
                
                encoded_content = base64.b64encode(content).decode('utf-8') # change the content just as the addedFirstTime case
                payload_update = {
                    'message': f'Updated file {file.name}',
                    'content': encoded_content,
                    'sha': sha
                }
                ack = requests.put(file_path, headers=headers, json=payload_update) # make a request to Github to update the file
                print ("ACK", ack)
                file.modified = False # no longer modified
                file.lastUpdated = datetime.now() # update the date of the file
                repoDB.lastUpdated = datetime.now() # update the repositories' last update date
                db.session.commit()

            # obtain the folder of the file
            if file.folderPath != file.repository_name + "/" and not file.deleted: # if the file is not in the root of the repository
                print ("Folder path", file.folderPath)
                folder = Folder.query.filter_by(path=file.folderPath[:-1], repository_name= file.repository_name).first()
                folder.addedFirstTime = False # no longer added for the first time
                folder.modified = False # no longer modified

        db.session.commit()
        return 0

    except FileNotFoundError as e:
        return 4

    except github.GithubException as e:
        return 5
        
    except Exception as e:
        print("Error -->", e)
        return 6
    