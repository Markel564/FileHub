import os
from ..models import User, Folder, File, Repository
from .getHash import sign_file, sign_folder

def check_file_system(repo):

    repo = Repository.query.filter_by(name=repo).first()

    if not repo:
        return False
    

    for file in repo.repository_files:

        file = File.query.filter_by(path=file.path).first()
        
        hash_of_file = sign_file(file.FileSystemPath)
        print (file.path, hash_of_file == file.shaHash)

    
    for folder in repo.repository_folders:

        folder = Folder.query.filter_by(path=folder.path).first()
        
        hash_of_folder = sign_folder(folder.FileSystemPath)
        print (folder.path, hash_of_folder == folder.shaHash)


    return True