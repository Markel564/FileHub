import os
from ..models import User, Folder, File, Repository
from .getHash import sign_file
from .. import db
from datetime import datetime
from .cloneRepo import windows_to_unix_path

def check_file_system(repo):

    repo = Repository.query.filter_by(name=repo).first()

    if not repo:
        return False
    

    # we have to check for new files in the file system that the user has entered manually
    # and add them to the database

    for root, dirs, files in os.walk(str(repo.FileSystemPath)+repo.name+"/"):
        

        if not root.startswith(repo.FileSystemPath+repo.name+"/.git"):

            for file in files:

                if file.startswith('~$'): # if the file is a temporary file, we don't want to add it to the database
                    continue

                full_file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(full_file_path, str(repo.FileSystemPath) + repo.name + "/")

                relative_file_path_with_repo = os.path.join(repo.name, relative_file_path)
                print("buscamos el archivo:", relative_file_path_with_repo, "con full path:", full_file_path)

                fileDB = File.query.filter_by(path=relative_file_path_with_repo).first()
                
                if not fileDB:
                    # we add the file to the database
                    folderPath = relative_file_path_with_repo.rsplit("/",1)[0] + "/"
                    FileSystemPath = windows_to_unix_path(full_file_path)
                    hash_of_file = sign_file(FileSystemPath)
                    file = File(name=file, path=relative_file_path_with_repo, repository_name=repo.name, 
                    lastUpdated=datetime.now(), modified=True, folderPath=folderPath, FileSystemPath=FileSystemPath, 
                    shaHash=hash_of_file, addedFirstTime=True)
                    db.session.add(file)

                    # we have to update the date of the folder where the file is located and the repository
                    father_dir = folderPath
                    print (f"Initial father_dir: {father_dir}")

                    while father_dir != repo.name + "/":
                        folder = Folder.query.filter_by(path=father_dir, repository_name=repo.name).first()

                        # there is a chance that the user created the directory manually, so we have to add it to the database
                        if not folder:
                            FileSystemPath = windows_to_unix_path(str(repo.FileSystemPath) + father_dir, True)
                            folder = Folder(path=father_dir[:-1], repository_name=repo.name, lastUpdated=datetime.now(), 
                            name=father_dir.rsplit("/",2)[1], modified=True, 
                            folderPath=father_dir.rsplit("/",2)[0] + "/", 
                            FileSystemPath=FileSystemPath)

                            print (f"Folder: {folder.name} with path {folder.path} and FileSystemPath {folder.FileSystemPath} and folderPath {folder.folderPath}")
                            db.session.add(folder)


                        else:
                            folder.lastUpdated = datetime.now()
                        
                        father_dir = father_dir.rsplit("/",2)[0] + "/"
                    
                    repo.lastUpdated = datetime.now()
   
        
            db.session.commit()
    
    # second, we have to check for modifications in the files that are already in the database
    for file_repo in repo.repository_files:

        print (f"file_repo: {file_repo.name}")
        file = File.query.filter_by(path=file_repo.path).first()
        hash_of_file = sign_file(file.FileSystemPath)

        # if the hashes are different, there is a modification in the file
        # and so, we have to update the database (NOT GITHUB YET)
        
        if hash_of_file != file.shaHash:
            file.modified = True
            file.shaHash = hash_of_file
            file.lastUpdated = datetime.now()

            # update the date of the folder where the file is located and the repository
            father_dir = file.folderPath
            
            while father_dir != repo.name + "/":
                print (f"father_dir: {father_dir}")
                folder = Folder.query.filter_by(path=father_dir[:-1], repository_name=repo.name).first()
                folder.lastUpdated = datetime.now()
                
                father_dir = father_dir.rsplit("/",2)[0] + "/"
            
            repo.lastUpdated = datetime.now()
        
        db.session.commit()
    return True