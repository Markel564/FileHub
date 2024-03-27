import os
from ..models import User, Folder, File, Repository
from .getHash import sign_file
from .. import db
from datetime import datetime
from .cloneRepo import windows_to_unix_path
from flask import session

def check_file_system(repo):

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return 1

    repo = Repository.query.filter_by(name=repo).first()

    if not repo:
        return 2
    
    if not repo.isCloned:
        return 3
    
    try:
        # we have to check for new files in the file system that the user has entered manually
        # and add them to the database
        # this includes files deleted, added or modified

        for root, dirs, files in os.walk(str(repo.FileSystemPath)+repo.name+"/"):
            

            if not root.startswith(repo.FileSystemPath+repo.name+"/.git"):

                for file in files:

                    if file.startswith('~$'): # if the file is a temporary file, we don't want to add it to the database
                        continue

                    full_file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(full_file_path, str(repo.FileSystemPath) + repo.name + "/")

                    relative_file_path_with_repo = os.path.join(repo.name, relative_file_path) # obtain the path of the file

                    fileDB = File.query.filter_by(path=relative_file_path_with_repo).first() 
                    
                    # ADDING NEW FILES TO THE DATABASE
                    if not fileDB: # if file not in database, that means the user has added a new file manually

                        # we add the file to the database
                        folderPath = relative_file_path_with_repo.rsplit("/",1)[0] + "/"
                        FileSystemPath = windows_to_unix_path(full_file_path)
                        hash_of_file = sign_file(FileSystemPath)

                        if not hash_of_file: # if the file is not found
                            return 4
                        
                        # create the file
                        file = File(name=file, path=relative_file_path_with_repo, repository_name=repo.name, 
                        lastUpdated=datetime.now(), modified=True, folderPath=folderPath, FileSystemPath=FileSystemPath, 
                        shaHash=hash_of_file, addedFirstTime=True)
                        db.session.add(file)

                        # we have to update the date of the folder where the file is located and the repository
                        father_dir = folderPath

                        while father_dir != repo.name + "/":
                            folder = Folder.query.filter_by(path=father_dir, repository_name=repo.name).first()

                            # there is a chance that the user created the directory manually, so we have to add it to the database
                            if not folder:
                                FileSystemPath = windows_to_unix_path(str(repo.FileSystemPath) + father_dir, True)
                                folder = Folder(path=father_dir[:-1], repository_name=repo.name, lastUpdated=datetime.now(), 
                                name=father_dir.rsplit("/",2)[1], modified=True, 
                                folderPath=father_dir.rsplit("/",2)[0] + "/", 
                                FileSystemPath=FileSystemPath)

                                db.session.add(folder)


                            else:
                                folder.lastUpdated = datetime.now()
                            
                            father_dir = father_dir.rsplit("/",2)[0] + "/"
                        
                        repo.lastUpdated = datetime.now()
    
            
                db.session.commit()
        
        # second, we have to check for modifications in the files that are already in the database
        for file_repo in repo.repository_files:

            file = File.query.filter_by(path=file_repo.path).first()
        
            hash_of_file = sign_file(file.FileSystemPath)

            if file.deleted: # if the file has been deleted, it will not be checked for modifications
                continue

            # DELETING FILES FROM THE DATABASE
            elif not hash_of_file: # if the file is not found, we have to delete it from the database, as it has been deleted
                file.deleted = True

                # we have to update the date of the folder where the file is located and the repository
                father_dir = file.folderPath
                update_dates(father_dir, repo.name)
                db.session.commit()

                continue
            
            # MODIFICATIONS IN FILES
            # if the hashes are different, there is a modification in the file
            # and so, we have to update the database (NOT GITHUB YET, this is done when user commits changes)
            
            if hash_of_file != file.shaHash:
                file.modified = True
                file.shaHash = hash_of_file
                file.lastUpdated = datetime.now()

                # update the date of the folder where the file is located and the repository
                father_dir = file.folderPath
                
                update_dates(father_dir, repo.name)
            
            db.session.commit()
        return 0

    except SQLAlchemyError:
        return 5
    except Exception:
        return 6


def update_dates(father_dir, repo_name):

    repo = Repository.query.filter_by(name=repo_name).first()  

    while father_dir != repo.name + "/":
        folder = Folder.query.filter_by(path=father_dir[:-1], repository_name=repo.name).first()
        folder.lastUpdated = datetime.now()
        father_dir = father_dir.rsplit("/",2)[0] + "/"
    
    repo.lastUpdated = datetime.now()
    db.session.commit()