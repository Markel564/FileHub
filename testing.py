from github import Github
from github import Auth
import github
from datetime import datetime
from git import Repo
import os
import yaml
from website.models import Repository
from website import db

def doesPathExist(path):
    isExist = os.path.exists(path)  
    
    if not isExist:
        print ("Does not exist")
        return False

    if not os.access(path, os.R_OK):
        print ("Not readable")
        return False
    if not os.access(path, os.W_OK):
        print ("Not writable")
        return False
    if not os.access(path, os.X_OK):
        print ("Not executable")
        return False
    
    # chech that it is a directory
    if not os.path.isdir(path):
        print ("Not a directory")
        return False
    
    return True


def windows_to_unix_path(windows_path):
    # Convert backslashes to forward slashes
    unix_path = windows_path.replace('\\', '/')
    
    # Check if the path starts with a drive letter
    if len(unix_path) > 1 and unix_path[1] == ':':
        drive_letter = unix_path[0].lower()
        path_without_drive = unix_path[2:]
        unix_path = '/mnt/' + drive_letter + path_without_drive

    return unix_path + "/"

def clone_repo(path, repoName):
    
    with open("config.yml", 'r') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)
    
    try:
        auth = Auth.Token(conf['api_token'])
        g = Github(auth=auth, base_url="https://api.github.com")

        user = g.get_user()

        repo = user.get_repo(repoName)

        # clone the repo in the path directory
        Repo.clone_from(repo.clone_url, path + repoName)

        return True
    except:
        return False

def check_isCloned(repoName):
    repoDB = Repository.query.filter_by(name=repoName).first()
    return repoDB.isCloned


if __name__ == "__main__":

    # Example usage
    windows_path = r'C:\Users\marke\Desktop\TFG\MarkHub'
    windows_path = r'C:\Users\\marke\Desktop\\TFG'
    unix_path = windows_to_unix_path(windows_path)
    print("Unix-style path:", unix_path)

    print (doesPathExist(unix_path))

    print (check_isCloned("TestingClone"))
    

