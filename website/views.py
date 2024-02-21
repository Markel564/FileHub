"""
This section contains the views of the website

Each view is a function for a specific route

The views are:

    - home: the main page of the website where the user can see his/her repositories
    - add: page that allows the user to add a new repository

"""

from flask import Blueprint, render_template, flash, request, jsonify, session, redirect
from . import db
from .models import User, Repository, Folder, File
views = Blueprint('views', __name__)
import os
from .pythonCode import *
from datetime import datetime

# HOME PAGE
@views.route('/', methods=['GET','POST'])
def home():

    if request.method == 'GET':

        
        if not add_user():  # error with the api token
            
            return render_template("error.html")

        

        
        # get the user from the database
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        
        # get the user's repositories
        repositories = get_repos()

        if not repositories:
            return render_template("error.html")
        
        # render template with the user's name, photo and repositories
        return render_template("home.html", header_name=user.username, avatar=user.avatarUrl, repositories=repositories)

    if request.method == 'POST':

        data = request.get_json()  # Get JSON data from the request (done through js)
        
        if data is None: # if no data was sent
            return jsonify({"status": "error"})
        
        type_message = data.get('type')


        if type_message == "eliminate":
            
            # we save the repo name to delete it later
            repo_name = data.get('repo_name') 
            session['repo_to_remove'] = repo_name

            return jsonify({"status": "ok"})

        elif type_message == "eliminate-confirm":

            # delete the repository
            ack = delete_repo()

            if ack:
                return jsonify({"status": "ok"})
            
            return jsonify({"status": "error"})

        elif type_message == "eliminate-cancel":
            
            # js handles cancelation (just eliminates the pop screen)
            return jsonify({"status": "ok"})

        elif type_message =="add":

            # js handles the redirection to /add
            return jsonify({"status": "ok"})

        elif type_message == "repo":
                        
            repoName = data.get('repo_name')
            repo_to_check = Repository.query.filter_by(name=repoName).first()

            if repo_to_check is None:
                return jsonify({"status": "errorNoRepo"})
            
            return jsonify({"status": "ok", "repoName": repoName + "/"})

        return jsonify({"status": "error"})



# ADD page
@views.route('/add', methods=['GET','POST'])
def add():

    if request.method == 'GET':
        # get the user's name and photo
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        return render_template("add.html", header_name=user.username, avatar=user.avatarUrl)
    
    else: # POST
        
        data = request.get_json()  

        if data is None:
            return render_template("generic_error.html")
        
        type_message = data.get('type')

        if type_message == "back":

            # js handles the redirection to /
            return jsonify({"status": "ok"})

        elif type_message == "create":
            
            # get the data from the POST request
            project_name = data.get('projectName')
            project_description = data.get('projectDescription')
            readme = data.get('readme')
            isPrivate = data.get('private')

            
            # check if there are no other repos with the same name
            repo = Repository.query.filter_by(name=project_name).first()

            if repo is not None:
                return jsonify({"status": "errorDuplicate"})

            # create the repo
            ack = add_repo(project_name, project_description, readme, isPrivate)
            
            if ack:
                flash("Repository created successfully", category='success')
                return jsonify({"status": "ok"})

            return jsonify({"status": "errorCreation"})
        
  


# REPO page
@views.route('/repo/<path:subpath>', methods=['GET','POST'])
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
            if not load_files_and_folders(repoName): # if there is an error with loading the files and folders
                    
                return jsonify({"status": "error"})
            files, folders = get_files_and_folders(repoName, subpath) # at first the path of the repository is the same as the name of the repository + '/'
            last_updated = Repository.query.filter_by(name=repoName).first().lastUpdated

            title = repoName
        else:
            # the path the files are alocated in github (the one we pass to load_files_and_folders)
            # is the subpath without the repoName
            # for example, if the subpath is 'repoName/folder1/folder2/', the path is 'folder1/folder2'

            if not load_files_and_folders(repoName, directory):
                return jsonify({"status": "error"})
            files, folders = get_files_and_folders(repoName, subpath +'/')
            last_updated = Folder.query.filter_by(repository_name=repoName, path=subpath).first().lastUpdated

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

            repoName = data.get('repoName')

            # search for the repository in the database
            repo = Repository.query.filter_by(name=repoName).first()
            if repo is None:
                return jsonify({"status": "error"})
            
            
            return jsonify({"status": "ok"})

        elif type_message == "clone-cancel":

            return jsonify({"status": "ok"})

        elif type_message == "clone-confirm":
            
            repoName = data.get('repoName')
            absolute_path = data.get('absolutePath')

            repo = Repository.query.filter_by(name=repoName).first()
            if repo is None:
                return jsonify({"status": "error"})
            
            if repo.isCloned:
                return jsonify({"status": "errorAlreadyCloned"})

            ack = clone_repo(repoName, absolute_path)
            print(ack)
            return jsonify({"status": "ok"})


@views.route('/upload-file', methods=['GET','POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        # Save the uploaded file to a directory on the server
        file.save('uploads/' + file.filename)
        # add the file to the database
        path = request.form.get('path')
        repoName = request.form.get('repoName')

        
        ack = add_file(repoName, file.filename, path) 
        if ack:
            flash("File uploaded successfully", category='success')
        else:
            return jsonify({'error': 'Error adding file to the database'}), 400

        return jsonify({'message': 'File uploaded successfully'})
    else:
        return jsonify({'error': 'No file received'}), 400


def reformat_date(last_updated):

    # if the date is None, return None
    if last_updated is None:
        return None


    # Sometimes, datetime.now() is delayed by a few seconds. In case that this happens
    # we will return 'just now' if the difference is less than 60 seconds
    if (datetime.now() - last_updated).total_seconds() < 0:
        return "just now"
    
    # if the number of years is +1, return years
    if (datetime.now() - last_updated).days >= 365:
        years = round((datetime.now() - last_updated).days // 365, 0)
        if years == 1:
            return "1 year ago"
        return str(years) + "years ago"

    # if the number of months is +1, return months
    elif (datetime.now() - last_updated).days >= 30:
        months = round((datetime.now() - last_updated).days // 30, 0)
        if months == 1:
            return "1 month ago"
        return str(months) + " months ago"

    # if the number of weeks is +1, return weeks
    elif (datetime.now() - last_updated).days >= 7:
        weeks = round((datetime.now() - last_updated).days // 7, 0)
        if weeks == 1:
            return "last week"
        return str(weeks) + " weeks ago"

    # if the number of days is +1, return days
    elif (datetime.now() - last_updated).days >= 1:
        days = round((datetime.now() - last_updated).days, 0)
        if days == 1:
            return "yesterday"
        return str(days) + " days ago"

    # if the number of hours is +1, return hours
    elif (datetime.now() - last_updated).total_seconds() >= 3600:
        hours = round((datetime.now() - last_updated).seconds // 3600, 0)
        if hours == 1:
            return "1 hour ago"
        return str(hours) + " hours ago"

    # if the number of minutes is +1, return minutes
    elif (datetime.now() - last_updated).seconds >= 60:
        minutes = round((datetime.now() - last_updated).seconds // 60, 0)
        if minutes == 1:
            return "1 minute ago"
        return str(minutes) + " minutes ago"
    
    else:
        seconds = round((datetime.now() - last_updated).seconds, 0)
        if seconds == 1:
            return "just now"
        return str(seconds) + " seconds ago"
    
    


    
    
        

    
 
    
    
        
    

        

            