from ..models import User, Repository, File
from .. import db
from github import Github, Auth
import github
import yaml
import requests
from flask import session
import os
from sqlalchemy.exc import SQLAlchemyError
import base64



def commit_changes(repoName, folderpath):
    
    user_id = session.get('user_id')
    userDB = User.query.filter_by(id=user_id).first()

    if not userDB:
        return 1
    
    repoDB = Repository.query.filter_by(name=repoName).first()

    if not repoDB:
        return 2
    
    if not repoDB.isCloned:
        return 3
    
    try:
        
        g = github.Github(userDB.githubG)
        user = g.get_user()

        repositories = user.get_repos()

        for repo in repositories:

            if repo.name == repoName:
                owner = repo.owner.login
                break

        base_url = f"https://api.github.com/repos/{owner}/{repoName}"

        headers = {
            'Authorization': f'token {userDB.githubG}',
            'Accept': 'application/vnd.github.v3+json'
        }


        for file in repoDB.repository_files:
            
            path_to_pass = file.folderPath.split('/')[1:]

            if path_to_pass[0] == '':
                path_to_pass = file.name
            else:
                path_to_pass = path_to_pass[0] + f"/{file.name}"
            file_path = f"{base_url}/contents/{path_to_pass}" # path to the particular file in Github
                
            # if the user deleted the file (from the local file system), eliminate it from Github
            if file.deleted:
                if not file.addedFirstTime: # if the file was not added for the first time, we can delete it from github (if it is, it is not in github yet, so we can't delete it)

                    response = requests.get(file_path, headers=headers)
                    if response.status_code != 200:
                        return 5
                    
                    file_data = response.json() # obtain the response in json format

                    # obtain the fields required
                    sha = file_data['sha']

                    # delete from github
                    payload_delete = {
                        'message': 'Deleted file',
                        'sha': sha
                    }

                    requests.delete(file_path, headers=headers, json=payload_delete)
                    db.session.delete(file)
                    db.session.commit()


                # also, if file is not in the filesystem, that means the user deleted it manually from the file system
                # however, if it does, we have to eliminate it from the file system
                if os.path.exists(file.FileSystemPath):
                    os.remove(file.FileSystemPath)

            # if the user created a file for the first time, upload it to Github
            elif file.addedFirstTime:

                with open(file.FileSystemPath, 'rb') as file_content:
                    content = file_content.read()
                
                encoded_content = base64.b64encode(content).decode('utf-8') # change the content to base64 as binary files are not allowed in a http json request

                payload_create = {
                    'message': 'Uploaded file',
                    'content': encoded_content
                }

                requests.put(file_path, headers=headers, json=payload_create)
                file.addedFirstTime = False # change the status of the file, as it is now in Github
                file.modified = False # no longer modified, for representation purposes
                db.session.commit() 

    
            # if user modified a file
            elif file.modified:  

                response = requests.get(file_path, headers=headers)
                if response.status_code != 200:
                    return 5
                
                file_data = response.json()
                # obtain the fields required (sha)
                sha = file_data['sha']

                with open(file.FileSystemPath, 'rb') as file_content:
                    content = file_content.read()
                
                encoded_content = base64.b64encode(content).decode('utf-8') # change the content just as the addedFirstTime case
                payload_update = {
                    'message': 'Updated file',
                    'content': encoded_content,
                    'sha': sha
                }
                requests.put(file_path, headers=headers, json=payload_update)
                file.modified = False # no longer modified
                
                db.session.commit()


        # also, we will delete the folders that the user deleted
        # it is not necessary to 'commit' the folder

        for folder in repoDB.repository_folders:

            if folder.deleted:
                db.session.delete(folder)
            
            if not folder.deleted:
                folder.addedFirstTime = False
                folder.modified = False


        db.session.commit()
        return 0

    except FileNotFoundError as e:
        return 4

    except github.GithubException as e:
        print(e)
        
        return 5
        
    except Exception as e:
        print(e)
        return 6
    