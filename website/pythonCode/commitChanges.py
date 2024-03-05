from ..models import User, Repository, File
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session


def commit_changes(repoName):
    
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

            if file.addedFirstTime:

                fileDB = File.query.filter_by(path=file.path).first()
                content = open(fileDB.FileSystemPath, 'rb').read()
                repo.create_file(file.path, "Uploaded file", content)
                file.addedFirstTime = False
                file.modified = False
                db.session.commit()

            if file.modified:

                fileDB = File.query.filter_by(path=file.path).first()
                content = open(fileDB.FileSystemPath, 'rb').read()
                repo.update_file(file.path, "Updated file", content, fileDB.shaHash)
                file.modified = False
                db.session.commit()
            
        return True

    except:
        return False