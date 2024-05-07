from ..models import User
from github import Github, Auth
import github
import yaml
from flask import session
import requests

def add_collaborator(repoName, collaboratorName, isAdmin, isReader, isWriter):

    user_id = session.get('user_id')

    userDB = User.query.filter_by(id=user_id).first()

    if not userDB:
        return 1
    
    if not isAdmin and not isReader and not isWriter:
        return 2 # no role was selected
    
    # check if the user is already a collaborator
    if collaboratorName == userDB.username:
        return 3 # can't add yourself as a collaborator
    
    # check if there is more than 1 role selected
    roles = [isAdmin, isReader, isWriter]
    if roles.count(True) > 1:
        return 4 # more than 1 role was selected

    if isAdmin:
        permission = "admin"
    elif isWriter:
        permission = "push"
    else:
        permission = "pull"

    try:

        g = Github(userDB.githubG)
        user = g.get_user()

        repositories = user.get_repos()
        for repo in repositories:
            if repo.name == repoName:
                owner = repo.owner.login
                break
                
        url = f"https://api.github.com/repos/{owner}/{repoName}/collaborators/{collaboratorName}"

        headers = {
            "Authorization": f"token {userDB.githubG}",
            "Accept": "application/vnd.github.v3+json"
        }

        data = {  # data to be sent to the API
            "permission": permission
        }

        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 204:
            return 5 # collaborator already exists

        if response.status_code == 201:
            return 0 # collaborator invited

        return 6 # error
    
    except Exception as e: 
        print(e)
        return 7
    