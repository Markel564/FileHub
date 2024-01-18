"""
Main file for github code

"""

from github import Github
from github import Auth
from datetime import datetime
from git import Repo
import os

def initialize_github():
    # returns a Github object
    # we use my personal access token to authenticate
    auth = Auth.Token("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")
    g = Github(auth=auth, base_url="https://api.github.com")

    return g




def delete_repo(name):

    g = initialize_github()
    user = g.get_user()
    repo = user.get_repo(name)
    repo.delete()
    print (f"REPO {name} DELETED")

    return True

    

if __name__ == "__main__":
    

    delete_repo("test")