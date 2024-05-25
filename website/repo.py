""" 
This section contains the view of the repository page

It represents each repository once the user has selected it
"""

from flask import Blueprint, render_template, flash, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Repository, Folder, File
import os
from .pythonCode import *
from flask_login import login_required


repository = Blueprint('repository', __name__)


# REPO page
@login_required
@repository.route('/<path:subpath>', methods=['GET','POST'])
def repo(subpath):

    # the path could be the name of the repository or a folder path such as 'repoName/folder1/folder2'
    repoName = subpath.split("/")[0]

    if request.method == 'GET': # if the user is accessing the repository page, show the files and folders of the repository

        if repoName is None: # if the repository does not exist (it will always be the first part of the subpath)
            return render_template("error.html")
        
        # get the user's name and photo
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

            
        root_of_project = False # if we are in the root of the repository
        directory = '/'.join(subpath.split("/")[1:]).rstrip('/') # the directory is the path of the folder in the repository

        if directory == '': # we are in a folder, if not, we are in the repository main page
            root_of_project = True
        
        if root_of_project: # we are in the root of the repository
            
            repo = Repository.query.filter_by(name=repoName).first() # get the repository from the database

            if not repo.loadedInDB: # if the repository is not loaded in the database, we load it
                
                ack = load_files_and_folders(repoName) # load the files and folders of the repository into the db
                if ack == 0:
                    pass
                elif ack == 1:
                    return render_template("error.html") 
                elif ack == 2:
                    flash("The Project does not exist!", category='error')
                    return render_template("error.html")
                else:
                    flash("There was an error!", category='error')
                    return redirect(url_for('homePage.home'))
         
                files, folders = get_files_and_folders(repoName, subpath) # at first the path of the repository is the same as the name of the repository + '/'
                
                if not files and not folders: # if there are no files or folders in the repository
                    flash ("There was an error!", category='error')
                    return redirect(url_for('homePage.home'))

                # when a get is produced, all the files and folders of the repository are loaded into the db (unless they are already loaded)
                folders_to_add = [] 
                folder_paths = []

                for folder in folders:
                    f = Folder.query.filter_by(repository_name=repoName, folderPath=folder[3]).first() # get the folder from the db

                    if not f.addedFirstTime: # if the folder is not loaded in the db, we add it to the list of folders to load
                        relative_path = folder[3].split('/',1)
                        folders_to_add.append(relative_path[1] + folder[0])
                        folder_paths.append(folder[3] + folder[0] + "/")


                while len(folders_to_add) > 0: # we are going to load into the db the files and folders of the repository for the folders that are in the path
                
                    folder = folders_to_add.pop(0) # get the folder to load

                    ack = load_files_and_folders(repoName, folder) # load the files and folders of the folder into the db
                    if ack == 0:
                        pass
                    elif ack == 1:
                        return render_template("error.html")
                    elif ack == 2:
                        flash("The Project does not exist!", category='error')
                        return render_template("error.html")
                    else:
                        flash("There was a file error!", category='error')
                        return render_template("error.html")

                    
                    files_in_db, folders_in_db = get_files_and_folders(repoName, folder_paths.pop(0)) # get the files and folders of the folder
                    if not files_in_db and not folders_in_db:
                        return render_template("error.html")

                    for folder in folders_in_db: # for each folder in the folder, add it to the list of folders to load
                        relative_path = folder[3].split('/',1)
                        folders_to_add.append(relative_path[1] + folder[0])
                        folder_paths.append(folder[3] + folder[0] + "/")

                last_updated = Repository.query.filter_by(name=repoName).first().lastUpdated # get the last updated date of the repository

                repo.loadedInDB = True # set the property of loaded asTrue
                db.session.commit()


            else: # the repository is already loaded in the database, so no need to be loaded again

                files, folders = get_files_and_folders(repoName, subpath) # get the files and folders of the repository
                last_updated = Repository.query.filter_by(name=repoName).first().lastUpdated

            title = repoName # the title of the page is the name of the repository


        else: # we are in a folder, and not in the root of the repository
            
            files, folders = get_files_and_folders(repoName, subpath +'/') # get the files and folders of the folder

            folder = Folder.query.filter_by(repository_name=repoName, path=subpath).first()
            last_updated = folder.lastUpdated # the last updated shown will be the last updated of the folder

            title = subpath.split("/")[-1] # the title of the page is the name of the folder, and not the repository


        for file in files:
            file[1] = reformat_date(file[1]) # reformat the dates (instead of a date, we will have X time ago)
                
            
        for folder in folders: # reformat the dates of the folders
            folder[1] = reformat_date(folder[1])

            
        #  change the date format to a more readable one
        last_updated = reformat_date(last_updated)
        
        # render the repository page
        return render_template("repo.html", title=title, header_name=repoName,avatar=user.avatarUrl, whole_path=subpath,
        files=files, folders=folders, last_updated=last_updated)


    else: # POST; a user has selected an option in the repository page
        
        data = request.get_json()  
        
        if data is None: # if no data was sent
            return jsonify({"status": "error"})
        
        type_message = data.get('type') # get the type of message
        
        if type_message == "back": # if the user wants to go back to the previous folder

            return jsonify({"status": "ok"}) # we will return the status ok, and the front end will redirect to the previous folder

        elif type_message == "open": # if the user wants to open a file
            
            # obtain the folder he/she wants to open
            folder = data.get('folder')
            folder_path = data.get('folderPath')
            
            # the repoName is the first part of the folder path
            repoName = folder_path.split("/")[0]
     
            if folder is None:
                return jsonify({"status": "error"})
            
            folders = Folder.query.filter_by(repository_name=repoName, folderPath=folder_path).all() # get the folders of the folder
    
            if folder not in [f.name for f in folders]: # if the folder is not in the list of folders
                return jsonify({"status": "error"})
            
            return jsonify({"status": "ok", "path": folder_path + folder}) # return the status ok and the path of the folder to open (js will redirect to the folder)

        elif type_message == "clone-confirm": # if the user wants to clone a repository
            
            # get the repository name and the path where the repository will be cloned
            repoName = data.get('repoName')
            absolute_path = data.get('absolutePath')

            ack = clone_repo(repoName, absolute_path)
            if ack == 0:
                flash("Project downloaded successfully", category='success')
                repo = Repository.query.filter_by(name=repoName).first()  # get the repository from the db
                repo.loadedInDB = False # we will change the loaded attribute and when a GET is made, the repository will be loaded again
                db.session.commit()
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
            elif ack == 3:
                flash("The Project is already downloaded!", category='error')
            elif ack == 4 or ack == 5 or ack == 7:
                flash("Unable to download the project", category='error')
            elif ack == 6:
                flash ("The path is not a directory!", category='error')
            else:
                flash("An unexpected error occurred!", category='error')

            return jsonify({"status": "ok"})

        
        elif type_message == "refresh-github": #to refresh the data based on the one in github (like a pull)
            
            repoName, folderPath = data.get('repoName'), data.get('folderPath')

            repo = Repository.query.filter_by(name=repoName).first()
            
            # we are going to load into the db the files and folders of the repository
            # that who have the folderPath as a prefix
            # e.g. f1/f2, we will load f1/f2/f3, f1/f2/f4, f1/f2, etc

            if folderPath == repoName + "/": # if we are in the root of the repository
                repo.loadedInDB = False # we will change the loaded attribute and when a GET is made, the repository will be loaded again
                db.session.commit()
                flash("Project updated from Github successfully", category='success')
                return jsonify({"status": "ok"})
            
            path = folderPath[:-1] # remove the last '/' from the folder path

            folder_origin = Folder.query.filter_by(repository_name=repoName, path=path).first() 

            if folder_origin is None:
                flash("Folder not found!", category='error')
                return jsonify({"status": "error"})
            
            path = path[len(repoName)+1:] # remove repoName/ from the folder path

            ack = load_files_and_folders(repoName, path) # load the files and folders of the folder into the db
            
            if ack == 0:
                pass
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
                return jsonify({"status": "error"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "error"})
        
            files, folders = get_files_and_folders(repoName, folderPath) # get the files and folders of the folder

            if not files and not folders: # if there are no files or folders in the folder, return an error
                return jsonify({"status": "error"})

            # load the files and folders of the folder
            folders_to_add = []
            folder_paths = []

            for folder in folders:
                relative_path = folder[3].split('/',1)
                folders_to_add.append(relative_path[1] + folder[0])
                folder_paths.append(folder[3] + folder[0] + "/")
            
            while len(folders_to_add) > 0:
                folder = folders_to_add.pop(0)

                ack = load_files_and_folders(repoName, folder) # load the files and folders of the folder into the db

                if ack == 0:
                    pass
                elif ack == 1:
                    return jsonify({"status": "error"})
                elif ack == 2:
                    flash("The Project does not exist!", category='error')
                    return jsonify({"status": "error"})
                else:
                    flash("An unexpected error occurred!", category='error')
                    return jsonify({"status": "error"})
                
                files_in_db, folders_in_db = get_files_and_folders(repoName, folder_paths.pop(0)) # get the files and folders of the folder

                if not files_in_db and not folders_in_db:
                    return jsonify({"status": "error"})

                for folder in folders_in_db: # for each folder in the folder, add it to the list of folders to load
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
            flash("Project updated from Github successfully", category='success') 
            return jsonify({"status": "ok"})

        
        elif type_message == "refresh-filesystem": # to refresh the data based on the one in the file system

            repoName = data.get('repoName') # get the repository name
            
            ack = check_file_system(repoName) # check the file system for new changes

            if ack == 0:
                flash("File system checked successfully", category='success')
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
            elif ack == 3:
                flash("The Project is not downloaded!", category='error')
            elif ack == 4:
                flash("An error with the file occurred!", category='error')
            else:
                flash("An unexpected error occurred!", category='error')
            return jsonify({"status": "ok"})

        elif type_message == "commit": # to commit the changes to the repository to the GitHub repository (like a push)
            
            repoName= data.get('repoName')

            # check that there is at least one file with a modification or that was added for the first time
            files = File.query.filter_by(repository_name=repoName).filter(File.folderPath.like(repoName + '%')).all()
            folders = Folder.query.filter_by(repository_name=repoName).filter(Folder.folderPath.like(repoName + '%')).all()


            modifications, insertions, deletions = False, False, False # flags to check if there are modifications, insertions or deletions
            for file in files:
                if file.modified:
                    modifications = True
                if file.addedFirstTime:
                    insertions = True
                if file.deleted:
                    deletions = True
            
            for folder in folders:
                if folder.modified:
                    modifications = True
                if folder.deleted:
                    deletions = True
                if folder.addedFirstTime:
                    insertions = True

            if len(files) == 0 and len(folders) == 0: # if there are no files or folders in the repository
                flash("No changes detected!", category='error')
                return jsonify({"status": "errorNoFiles"})
            
            # if there are no files modified or added (or deletions), do not commit
            if not modifications and not insertions and not deletions:
                flash("No changes detected!", category='error')
                return jsonify({"status": "errorNoFiles"})

            ack = commit_changes(repoName) # commit the changes to the repository

            if ack == 0:
                flash("Changes sent to GitHub successfully", category='success')
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
            elif ack == 3:
                flash("The Project is not downloaded!", category='error')
            else:
                flash("An unexpected error occurred!", category='error')
            return jsonify({"status": "ok"})

        
        elif type_message == "delete-file": # to delete a file
            
            # get the repository name, the folder path and the file name
            repoName, folderPath, fileName = data.get('repoName'), data.get('folderPath'), data.get('fileName')

            if folderPath == "/": # if we are in the root of the repository
                path = repoName+"/"+fileName # the path is the repository name + the file name. E.g. repoName/file1
                inRoot = True
            else:
                path = repoName+"/"+folderPath+fileName # the path is the repository name + the folder path + the file name. E.g. repoName/folder1/file1

            ack = delete_file(repoName, path, fileName) # delete the file
 
            if ack == 0:
                flash("File deleted successfully", category='success')
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
            elif ack == 3:
                flash("The Project is not downloaded!", category='error')
            elif ack == 4:
                flash("File not found!", category='error')
            elif ack == 5:
                flash("The file is already deleted!", category='error')
            else:
                flash("An unexpected error occurred!", category='error')
            return jsonify({"status": "ok"})

        elif type_message == "delete-folder": # to delete a folder
            
            # get the repository name, the folder path and the folder name
            repoName, folderPath, folderName = data.get('repoName'), data.get('folderPath'), data.get('folderName')

            if folderPath == "/": # if we are in the root of the repository
                path = repoName+"/"+folderName # the path is the repository name + the folder name. E.g. repoName/folder1
            else:
                path = repoName+"/"+folderPath+folderName # the path is the repository name + the folder path + the folder name. E.g. repoName/folder1/folder2
            
            ack = delete_folder(repoName, path, folderName) # delete the folder

            if ack == 0:
                flash("Folder deleted successfully", category='success')
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
            elif ack == 3:
                flash("The Project is not downloaded!", category='error')
            elif ack == 4:
                flash("Folder not found!", category='error')
            elif ack == 5:
                flash("The folder is already deleted!", category='error')
            else:
                flash("An unexpected error occurred!", category='error')
            return jsonify({"status": "ok"})

        
        elif type_message == "create-folder": # to create a folder
            
            # get the repository name, the folder name and the folder path
            folderName, repoName, folderPath = data.get('folderName'), data.get('repoName'), data.get('folderPath')

            if folderPath == "/": # if we are in the root of the repository
                path = repoName + "/" + folderName # the path is the repository name + the folder name. E.g. repoName/folder1
            else:
                path = repoName + "/" + folderPath + folderName # if not, the path is the repository name + the folder path + the folder name. E.g. repoName/folder1/folder2

            ack = create_folder(repoName, folderName, path) # create the folder

            if ack == 0:
                flash("Folder created successfully", category='success')   
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
            elif ack == 3:
                flash("The Project is not downloaded!", category='error')
            elif ack == 4:
                flash("Folder already exists!", category='error')
            elif ack == 5:
                flash("Error creating the folder in the file system!", category='error')
            else:
                flash("An unexpected error occurred!", category='error')

            return jsonify({"status": "ok"})
 
        elif type_message == "add-people": # to add people to the repository
            
            repoName = data.get('repoName')
            # just return the url of the collaboration page
            return jsonify({"status": "ok", "url": url_for('collabPage.collaboration', repoName=repoName)})

            


