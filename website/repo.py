from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User, Repository, Folder, File
import os
from .pythonCode import *


repository = Blueprint('repository', __name__)


# REPO page
@repository.route('/<path:subpath>', methods=['GET','POST'])
def repo(subpath):
    # the path could be the name of the repository or a folder path such as 'repoName/folder1/folder2'
    repoName = subpath.split("/")[0]

    if request.method == 'GET':

        if repoName is None:
            return render_template("generic_error.html")
        
        # get the user's name and photo
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

            
        root_of_project = False
        directory = '/'.join(subpath.split("/")[1:]).rstrip('/')

        if directory == '': # we are in a folder, if not, we are in the repository main page
            root_of_project = True
            
        if root_of_project:
            
            repo = Repository.query.filter_by(name=repoName).first()

            if not repo.loadedInDB: # if the repository is not loaded in the database, we load it
                
                ack = load_files_and_folders(repoName) # load the files and folders of the repository into the db

                if ack == 0:
                    pass
                elif ack == 1:
                    flash("User not identified!", category='error')
                    return render_template("generic_error.html")
                elif ack == 2:
                    flash("The repository does not exist!", category='error')
                    return render_template("generic_error.html")
                elif ack == 3:
                    flash("There was a file error!", category='error')
                    return render_template("generic_error.html")
                elif ack == 4:
                    flash("There was a github error!", category='error')
                    return render_template("generic_error.html")
                elif ack == 5:
                    flash("There was an error with the database!", category='error')
                    return render_template("generic_error.html")
                else:
                    flash("An unexpected error occurred!", category='error')
                    return render_template("generic_error.html")
         
                files, folders = get_files_and_folders(repoName, subpath) # at first the path of the repository is the same as the name of the repository + '/'
                
                if not files and not folders:
                    return render_template("error.html")
        
                folders_to_add = []
                folder_paths = []

                for folder in folders:
                    relative_path = folder[3].split('/',1)
                    folders_to_add.append(relative_path[1] + folder[0])
                    folder_paths.append(folder[3] + folder[0] + "/")

                while len(folders_to_add) > 0: # we are going to load into the db the files and folders of the repository for the folders that are in the path
                
                    folder = folders_to_add.pop(0)

                    ack = load_files_and_folders(repoName, folder)

                    if ack == 0:
                        pass
                    elif ack == 1:
                        flash("User not identified!", category='error')
                        return render_template("generic_error.html")
                    elif ack == 2:
                        flash("The repository does not exist!", category='error')
                        return render_template("generic_error.html")
                    elif ack == 3:
                        flash("There was a file error!", category='error')
                        return render_template("generic_error.html")
                    elif ack == 4:
                        flash("There was a github error!", category='error')
                        return render_template("generic_error.html")
                    elif ack == 5:
                        flash("There was an error with the database!", category='error')
                        return render_template("generic_error.html")
                    else:
                        flash("An unexpected error occurred!", category='error')
                        return render_template("generic_error.html")

                    
                    files_in_db, folders_in_db = get_files_and_folders(repoName, folder_paths.pop(0))

                    if not files_in_db and not folders_in_db:
                        return render_template("error.html")

                    for folder in folders_in_db:
                        relative_path = folder[3].split('/',1)
                        folders_to_add.append(relative_path[1] + folder[0])
                        folder_paths.append(folder[3] + folder[0] + "/")

                last_updated = Repository.query.filter_by(name=repoName).first().lastUpdated

                repo.loadedInDB = True

                db.session.commit()

            else: # the repository is already loaded in the database, so no need to be loaded again

                files, folders = get_files_and_folders(repoName, subpath)
                last_updated = Repository.query.filter_by(name=repoName).first().lastUpdated

            title = repoName


        else: # we are in a folder, and not in the root of the repository

            files, folders = get_files_and_folders(repoName, subpath +'/')
            folder = Folder.query.filter_by(repository_name=repoName, path=subpath).first()
            last_updated = folder.lastUpdated

            title = subpath.split("/")[-1]


        for file in files:
            file[1] = reformat_date(file[1])
                
            
        for folder in folders:
            folder[1] = reformat_date(folder[1])

            
        #  change the date format to a more readable one
        last_updated = reformat_date(last_updated)
        
        return render_template("repo.html", title=title, header_name=repoName,avatar=user.avatarUrl, whole_path=subpath,
        files=files, folders=folders, last_updated=last_updated)

       


    else: # POST
        
        data = request.get_json()  
        
        if data is None: # if no data was sent
            return jsonify({"status": "error"})
        
        type_message = data.get('type')
        
        if type_message == "back":

            return jsonify({"status": "ok"})

        elif type_message == "open":

            folder = data.get('folder')
            folder_path = data.get('folderPath')

            
            
            # the repoName is the first part of the folder path
            repoName = folder_path.split("/")[0]
     
            if folder is None:
                return jsonify({"status": "error"})
            

            folders = Folder.query.filter_by(repository_name=repoName, folderPath=folder_path).all()


    
            if folder not in [f.name for f in folders]:
                return jsonify({"status": "error"})
            
            return jsonify({"status": "ok", "path": folder_path + folder})

        elif type_message == "clone-request":

            repoName, option = data.get('repoName'), data.get('option')

            # search for the repository in the database
            repo = Repository.query.filter_by(name=repoName).first()
            if repo is None:
                return jsonify({"status": "error"})

            if option == "SYNCHRONIZE": #user wants to clone repository with file system
                return jsonify({"status": "ok"})
            
            # user wants to stop clonation
            repo.isCloned = False
            db.session.commit()
            flash("Repository not synchronized anymore with file system", category='success')
            return jsonify({"status": "ok", "option": "Stop"}) 

        elif type_message == "clone-cancel":

            return jsonify({"status": "ok"})

        elif type_message == "clone-confirm":
 
            repoName = data.get('repoName')
            absolute_path = data.get('absolutePath')


            ack = clone_repo(repoName, absolute_path)

            if ack == 0:
                flash("Repository cloned successfully", category='success')
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The repository does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3:
                flash("The repository is already cloned!", category='error')
                return jsonify({"status": "errorRepoAlreadyCloned"})
            elif ack == 4:
                flash("An error with the file occurred!", category='error')
                return jsonify({"status": "fileError"})
            elif ack == 5:
                flash("There was a permission error!", category='error')
                return jsonify({"status": "permissionError"})
            elif ack == 6:
                flash ("The path is not a directory!", category='error')
                return jsonify({"status": "notDirectoryError"})
            elif ack == 7:
                flash("There was a Github error!", category='error')
                return jsonify({"status": "githubError"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})


        
        elif type_message == "refresh-github": #to refresh the data based on the one in github (like a pull)

            repoName, folderPath = data.get('repoName'), data.get('folderPath')

            repo = Repository.query.filter_by(name=repoName).first()
            

            # we are going to load into the db the files and folders of the repository
            # that who have the folderPath as a prefix
            # e.g. f1/f2, we will load f1/f2/f3, f1/f2/f4, f1/f2, etc

            if folderPath == repoName + "/": # if we are in the root of the repository
                repo.loadedInDB = False # we will change the loaded attribute and when a GET is made, the repository will be loaded again
                db.session.commit()

                return jsonify({"status": "ok"})
            
            path = folderPath[:-1] # remove the last '/' from the folder path

            folder_origin = Folder.query.filter_by(repository_name=repoName, path=path).first() 

            if folder_origin is None:
                # flash something
                return jsonify({"status": "error"})
            
            path = path[len(repoName)+1:] # remove repoName/ from the folder path

            ack = load_files_and_folders(repoName, path) # load the files and folders of the folder into the db

            if ack == 0:
                pass
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The repository does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3:
                flash("There was a file error!", category='error')
                return jsonify({"status": "errorFile"})
            elif ack == 4:
                flash("There was a github error!", category='error')
                return jsonify({"status": "errorGithub"})
            elif ack == 5:
                flash("There was an error with the database!", category='error')
                return jsonify({"status": "errorDB"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})


            files, folders = get_files_and_folders(repoName, folderPath) # get the files and folders of the folder

            if not files and not folders:
                return jsonify({"status": "error"})

            folders_to_add = []
            folder_paths = []

            for folder in folders:
                relative_path = folder[3].split('/',1)
                folders_to_add.append(relative_path[1] + folder[0])
                folder_paths.append(folder[3] + folder[0] + "/")
            
            while len(folders_to_add) > 0:
                folder = folders_to_add.pop(0)

                ack = load_files_and_folders(repoName, folder)

                if ack == 0:
                    pass
                elif ack == 1:
                    flash("User not identified!", category='error')
                    return jsonify({"status": "error"})
                elif ack == 2:
                    flash("The repository does not exist!", category='error')
                    return jsonify({"status": "error"})
                elif ack == 3:
                    flash("There was a file error!", category='error')
                    return jsonify({"status": "error"})
                elif ack == 4:
                    flash("There was a github error!", category='error')
                    return jsonify({"status": "error"})
                elif ack == 5:
                    flash("There was an error with the database!", category='error')
                    return jsonify({"status": "error"})
                else:
                    flash("An unexpected error occurred!", category='error')
                    return jsonify({"status": "error"})

                
                files_in_db, folders_in_db = get_files_and_folders(repoName, folder_paths.pop(0))

                if not files_in_db and not folders_in_db:
                    return jsonify({"status": "error"})

                for folder in folders_in_db:
                    relative_path = folder[3].split('/',1)
                    folders_to_add.append(relative_path[1] + folder[0])
                    folder_paths.append(folder[3] + folder[0] + "/")
                
                

            # also, we have to update the lastUpdated attribute of the folder and all the father folders
            father_dir = repoName + "/" + path + "/" # the father directory of the folder
            # eliminate the last folder from the path
            father_dir = father_dir.rsplit("/",2)[0] + "/"
 
            while father_dir != repoName + "/":
                father_folder = Folder.query.filter_by(repository_name=repoName, folderPath=father_dir).first()
                father_folder.lastUpdated = folder_origin.lastUpdated
                
                father_dir = father_dir.rsplit("/",2)[0] + "/" 

            db.session.commit()
            return jsonify({"status": "ok"})

        
        elif type_message == "refresh-filesystem":


            repoName = data.get('repoName')
            
            ack = check_file_system(repoName)

            if ack == 0:
                flash("File system checked successfully", category='success')
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The repository does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3:
                flash("The repository is not cloned!", category='error')
                return jsonify({"status": "errorRepoNotCloned"})
            elif ack == 4:
                flash("An error with the file occurred!", category='error')
                return jsonify({"status": "fileError"})
            elif ack == 5:
                flash("Error adding file to the database!", category='error')
                return jsonify({"status": "errorDB"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})



        elif type_message == "commit":

            repoName, folderPath = data.get('repoName'), data.get('folderPath') 

            # check that there is at least one file with a modification or that was added for the first time
            files = File.query.filter_by(repository_name=repoName, folderPath=folderPath).all()
            folders = Folder.query.filter_by(repository_name=repoName, folderPath=folderPath).all()
            
            modifications, insertions, deletions = False, False, False
            for file in files:
                print (file.name, file.modified, file.addedFirstTime, file.deleted)
                if file.modified:
                    modifications = True
                if file.addedFirstTime:
                    insertions = True
                if file.deleted:
                    deletions = True
            
            for folder in folders:
                print (folder.name, folder.modified, folder.addedFirstTime, folder.deleted)
                if folder.modified:
                    modifications = True
                if folder.deleted:
                    deletions = True
                if folder.addedFirstTime:
                    insertions = True

            if len(files) == 0 and len(folders) == 0:
                flash("No changes to commit", category='error')
                return jsonify({"status": "errorNoFiles"})
            
            # if there are no files modified or added (or deletions), do not commit
            if not modifications and not insertions and not deletions:
                flash("No changes detected", category='error')
                return jsonify({"status": "errorNoFiles"})

            ack = commit_changes(repoName, folderPath)

            if ack == 0:
                flash("Changes sent to GitHub successfully", category='success')
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The repository does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3:
                flash("The repository is not cloned!", category='error')
                return jsonify({"status": "errorRepoNotCloned"})
            elif ack == 4:
                flash("There was an error with a file!", category='error')
                return jsonify({"status": "fileError"})
            elif ack == 5:
                flash("There was a Github error!", category='error')
                return jsonify({"status": "githubError"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})
            

        
        elif type_message == "delete-file":
            
            repoName, folderPath, fileName = data.get('repoName'), data.get('folderPath'), data.get('fileName')


            if folderPath == "/": # if we are in the root of the repository
                path = repoName+"/"+fileName
                inRoot = True
            else:
                path = repoName+"/"+folderPath+fileName

            ack = delete_file(repoName, path, fileName)

            if ack == 0:
                flash("File deleted successfully", category='success')
                repo = Repository.query.filter_by(name=repoName).first()
                repo.loadedInDB = False # we will change the loaded attribute and when a GET is made, the repository will be loaded again
                                        # showing the changes made
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The repository does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3:
                flash("The repository is not cloned!", category='error')
                return jsonify({"status": "errorRepoNotCloned"})
            elif ack == 4:
                flash("File not found!", category='error')
                return jsonify({"status": "fileError"})
            elif ack == 5:
                flash("The file is already deleted! Commit the changes to send them!", category='error')
                return jsonify({"status": "errorFileAlreadyDeleted"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})


        elif type_message == "delete-folder":
  
            repoName, folderPath, folderName = data.get('repoName'), data.get('folderPath'), data.get('folderName')

            if folderPath == "/":
                path = repoName+"/"+folderName
            else:
                path = repoName+"/"+folderPath+folderName
            
            ack = delete_folder(repoName, path, folderName)

            if ack == 0:
                flash("Folder deleted successfully", category='success')
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The repository does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3:
                flash("The repository is not cloned!", category='error')
                return jsonify({"status": "errorRepoNotCloned"})
            elif ack == 4:
                flash("Folder not found!", category='error')
                return jsonify({"status": "folderError"})
            elif ack == 5:
                flash("The folder is already deleted! Commit the changes to send them!", category='error')
                return jsonify({"status": "errorFolderAlreadyDeleted"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})


        elif type_message == "open-file":

            return jsonify({"status": "ok"})

            # repoName, folderPath, fileName = data.get('repoName'), data.get('folderPath'), data.get('fileName')

            # if folderPath == "/":  # if we are in the root of the repository
            #     path = repoName+"/"+fileName
            # else:
            #     path = repoName+"/"+folderPath+fileName

            # ack = open_file(repoName, path)

            # if ack == 0:
            #     return jsonify({"status": "ok"})
            # elif ack == 1:
            #     flash("User not identified!", category='error')
            #     return jsonify({"status": "errorUser"})
            # elif ack == 2:
            #     flash("The repository does not exist!", category='error')
            #     return jsonify({"status": "errorRepoDoesNotExist"})
            # elif ack == 3:
            #     flash("The repository is not cloned!", category='error')
            #     return jsonify({"status": "errorRepoNotCloned"})
            # elif ack == 4:
            #     flash("File not found!", category='error')
            #     return jsonify({"status": "fileError"})
            # elif ack == 5:
            #     flash("Error opening the file!", category='error')
            #     return jsonify({"status": "fileError"})
            # elif ack == 6:
            #     flash("The operating system is not supported!", category='error')
            #     return jsonify({"status": "errorOS"})
            # else:
            #     flash("An unexpected error occurred!", category='error')
            #     return jsonify({"status": "unexpectedError"})


        elif type_message == "new-folder-request":

            return jsonify({"status": "ok"})
        
        elif type_message == "create-folder":

            folderName, repoName, folderPath = data.get('folderName'), data.get('repoName'), data.get('folderPath')

            if folderPath == "/":
                path = repoName + "/" + folderName
            else:
                path = repoName + "/" + folderPath + folderName

            ack = create_folder(repoName, folderName, path)

            if ack == 0:
                flash("Folder created successfully", category='success')
                return jsonify({"status": "ok"})    
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The repository does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3:
                flash("The repository is not cloned!", category='error')
                return jsonify({"status": "errorRepoNotCloned"})
            elif ack == 4:
                flash("Folder already exists!", category='error')
                return jsonify({"status": "errorFolderExists"})
            elif ack == 5:
                flash("Error creating the folder in the file system!", category='error')
                return jsonify({"status": "errorFolder"})
            elif ack == 6:
                flash("Error adding the folder to the database!", category='error')
                return jsonify({"status": "errorDB"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})

            return jsonify({"status": "ok"})

        elif type_message == "cancel-folder":

            return jsonify({"status": "ok"})