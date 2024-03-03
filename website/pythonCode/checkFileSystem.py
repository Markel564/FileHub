import os
from ..models import User, Folder, File, Repository
from .getHash import sign_file, sign_folder
from .. import db
from datetime import datetime

def check_file_system(repo):

    repo = Repository.query.filter_by(name=repo).first()

    if not repo:
        return False
    

    for file in repo.repository_files:

        file = File.query.filter_by(path=file.path).first()
        hash_of_file = sign_file(file.FileSystemPath)

        # if the hashes are different, there is a modification in the file
        # and so, we have to update the database (NOT GITHUB YET)
        
        if hash_of_file != file.shaHash:
            file.modified = True
            file.shaHash = hash_of_file
            file.lastUpdated = datetime.now()

            # update the date of the folder where the file is located and the repository
            print ("Initially, the folder path is", file.folderPath)
            father_dir = file.folderPath

            while father_dir != repo.name + "/":
                print ("Searching for the folder", father_dir)
                folder = Folder.query.filter_by(path=father_dir, repository_name=repo.name).first()
                folder.lastUpdated = datetime.now()
                
                father_dir = father_dir.rsplit("/",2)[0] + "/"
            
            repo.lastUpdated = datetime.now()
        
        db.session.commit()


    return True