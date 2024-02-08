"""
This section contains the views of the website

Each view is a function for a specific route

The views are:

    - home: the main page of the website where the user can see his/her repositories
    - add: page that allows the user to add a new repository

"""

from flask import Blueprint, render_template, flash, request, jsonify, session, redirect
from . import db
from .models import User, Repository
views = Blueprint('views', __name__)
import os
from .pythonCode import add_user, get_repos, delete_repo, add_repo, load_files_and_folders, get_files_and_folders
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
            
            return jsonify({"status": "ok", "repoName": repoName})

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
@views.route('/repo/<repoName>', methods=['GET','POST'])
def repo(repoName):

    if request.method == 'GET':
        
        if repoName is None:
            return render_template("generic_error.html")
        
        # get the user's name and photo
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

        if not load_files_and_folders(repoName): # if there is an error with loading the files and folders
            
            return jsonify({"status": "error"})

    

        files, folders = get_files_and_folders(repoName)

        for file in files:
            file[1] = reformat_date(file[1])
            
        
        for folder in folders:
            folder[1] = reformat_date(folder[1])

        last_updated = Repository.query.filter_by(name=repoName).first().lastUpdated
        
        #  change the date format to a more readable one
        last_updated = reformat_date(last_updated)

        
        return render_template("repo.html", repo=repoName, header_name=repoName, avatar=user.avatarUrl, files=files, folders=folders, last_updated=last_updated)
    
    else:

        data = request.get_json()  
        
        if data is None: # if no data was sent
            return jsonify({"status": "error"})
        
        type_message = data.get('type')
        

        if type_message == "back":

            return jsonify({"status": "ok"})
            


def reformat_date(last_updated):

    # if the date is None, return None
    if last_updated is None:
        return None

    # if the date is None, return None
    if last_updated is None:
        return None
    
    # if the number of years is +1, return years
    if (datetime.now() - last_updated).days > 365:
        years = round((datetime.now() - last_updated).days // 365, 0)
        if years == 1:
            return "1 year ago"
        return str(years) + "years ago"

    # if the number of months is +1, return months
    elif (datetime.now() - last_updated).days > 30:
        months = round((datetime.now() - last_updated).days // 30, 0)
        if months == 1:
            return "1 month ago"
        return str(months) + " months ago"

    # if the number of weeks is +1, return weeks
    elif (datetime.now() - last_updated).days > 7:
        weeks = round((datetime.now() - last_updated).days // 7, 0)
        if weeks == 1:
            return "last week"
        return str(weeks) + " weeks ago"

    # if the number of days is +1, return days
    elif (datetime.now() - last_updated).days > 1:
        days = round((datetime.now() - last_updated).days, 0)
        if days == 1:
            return "yesterday"
        return str(days) + " days ago"

    # if the number of hours is +1, return hours
    elif (datetime.now() - last_updated).seconds > 3600:
        hours = round((datetime.now() - last_updated).seconds // 3600, 0)
        if hours == 1:
            return "1 hour ago"
        return str(hours) + " hours ago"

    # if the number of minutes is +1, return minutes
    elif (datetime.now() - last_updated).seconds > 60:
        minutes = round((datetime.now() - last_updated).seconds // 60, 0)
        if minutes == 1:
            return "1 minute ago"
        return str(minutes) + " minutes ago"
    
    else:
        seconds = round((datetime.now() - last_updated).seconds, 0)
        if seconds == 1:
            return "1 second ago"
        return str(seconds) + " seconds ago"
    
    


    
    
        

    
 
    
    
        
    

        

            