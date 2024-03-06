from ..models import User, Repository, File
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session


def commit_changes(repoName, folderpath):
    
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return False
    
    try:

        repoDB = Repository.query.filter_by(name=repoName).first()

        if not repoDB:
            return False
        
        g = github.Github(user.githubG)
        user = g.get_user()
        repo = user.get_repo(repoName)

        for file in repoDB.repository_files:
            # if the file is modified, we have to commit the changes

            if file.folderPath == folderpath:

                if file.addedFirstTime:
                    
                    print (f"File {file.path} with name {file.name} added for the first time and systempath {file.FileSystemPath}!")
                    path_to_pass = file.folderPath.split('/')[1:]
                    if path_to_pass[0] == '':
                        path_to_pass = file.name
                    else:
                        path_to_pass = path_to_pass[0] + f"/{file.name}"
                    print (path_to_pass)
                    content = open(file.FileSystemPath, 'rb').read()
                    repo.create_file(path_to_pass, "Uploaded file", content)
                    file.addedFirstTime = False
                    file.modified = False
    

                elif file.modified:
                    
                    print (f"File {file.path} with name {file.name} and systempath {file.FileSystemPath} modified!")
                    path_to_pass = file.folderPath.split('/')[1:]
                    if path_to_pass[0] == '':
                        path_to_pass = file.name
                    else:
                        path_to_pass = path_to_pass[0] + f"/{file.name}"
                    print (path_to_pass)

                    file_GB = repo.get_contents(f"{path_to_pass}")
                    
                    content = open(file.FileSystemPath, 'rb').read()
                    repo.update_file(path_to_pass, "Updated file", content, file_GB.sha)
                    file.modified = False
        
        db.session.commit()
        return True

    except Exception as e:
        print (e)
        return False