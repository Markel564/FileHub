from github import Github
from github import Auth
import github
from datetime import datetime
from git import Repo
import os
from .website.models import User, Repository, Folder, File

from sqlalchemy import create_engine, MetaData

engine = create_engine('sqlite:///database.db', echo=True)

metadata = MetaData()
metadata.reflect(bind=engine)

def see_database():

    for table in metadata.tables.values():
        print(f"Table: {table.name}")
        for foreign_key in table.foreign_keys:
            print(f"  - Foreign Key: {foreign_key}")
        for column in table.columns:
            print(f"  - Column: {column.name}, Type: {column.type}")

def initialize_github():
    # returns a Github object
    # we use my personal access token to authenticate
    auth = Auth.Token("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")
    g = Github(auth=auth, base_url="https://api.github.com")

    return g




def see_repo(name, path="", parent_folder=""):
    g = initialize_github()
    user = g.get_user()
    repo = user.get_repo(name)
    
    # Get the contents of the current path within the repo
    contents = repo.get_contents(path)

    for content in contents:
        if content.type == "dir":
            # Get the name of the directory
            directory_name = content.name

            # Determine the full path of the directory
            full_path = content.path


            # Print the directory name and its parent folder
            print(f"Directory: {directory_name}, Path: {full_path}")

            # Recursively call see_repo for the subdirectory
            see_repo(name, path=full_path, parent_folder=directory_name)
    
    return True


def get_content(repoName):

    # search for the repo in the db and get all the folders associated with it
    folders = Folder.query.filter_by(repository_name=repoName).all()

    print ("folders: ", folders)



if __name__ == "__main__":
    

    # see_repo("IoT_project")
    # see_database()
    get_content("Dam2_project")