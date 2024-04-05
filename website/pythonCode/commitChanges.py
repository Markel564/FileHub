from ..models import User, Repository, File
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
import os
from sqlalchemy.exc import SQLAlchemyError



def commit_changes(repoName, folderpath):
    
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return 1
    
    repoDB = Repository.query.filter_by(name=repoName).first()

    if not repoDB:
        return 2
    
    if not repoDB.isCloned:
        return 3
    
    try:
        
        g = github.Github(user.githubG)
        user = g.get_user()
        repo = user.get_repo(repoName)

        for file in repoDB.repository_files:
            
            # if the file is modified, we have to commit the changes
                
            # if the user deleted the file (from the local file system), eliminate it from github
            if file.deleted:
                print (f"DELETING FILE {file.name}")
                if not file.addedFirstTime:
                    path_to_pass = file.folderPath.split('/')[1:]
                        
                    if path_to_pass[0] == '':
                        path_to_pass = file.name
                    else:
                        path_to_pass = '/'.join(path_to_pass) + f"{file.name}"
    
                    file_GB = repo.get_contents(f"{path_to_pass}")

                    repo.delete_file(file_GB.path, "Deleted file", file_GB.sha)
                    # we can now delete the file from the db
                    db.session.delete(file)
                    db.session.commit()

                # also, if file is not in the filesystem, that means the user deleted it manually from the file system
                # however, if it does, we have to eliminate it from the file system
                if os.path.exists(file.FileSystemPath):
                    os.remove(file.FileSystemPath)

            # if the user created a file for the first time
            elif file.addedFirstTime:
                print (f"UPLOADING FILE {file.name}")
                path_to_pass = file.folderPath.split('/')[1:]
                if path_to_pass[0] == '':
                    path_to_pass = file.name
                else:
                    path_to_pass = '/'.join(path_to_pass) + f"{file.name}"
                    
                content = open(file.FileSystemPath, 'rb').read()

                repo.create_file(path_to_pass, "Uploaded file", content)
                file.addedFirstTime = False
                file.modified = False
                    
                db.session.commit()
    
            # if user modified a file
            elif file.modified:
                print (f"UPDATING FILE {file.name}")
                path_to_pass = file.folderPath.split('/')[1:]
                if path_to_pass[0] == '':
                    path_to_pass = file.name
                else:
                    path_to_pass = path_to_pass[0] + f"/{file.name}"

                file_GB = repo.get_contents(f"{path_to_pass}")
                    
                content = open(file.FileSystemPath, 'rb').read()
                repo.update_file(path_to_pass, "Updated file", content, file_GB.sha)
                file.modified = False

        # also, we will delete the folders that the user deleted
        # it is not necessary to 'commit' the folder

        for folder in repoDB.repository_folders:

            if folder.deleted:
                print (f"DELETING FOLDER {folder.path} (first time)")
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
    