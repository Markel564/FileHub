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
from .pythonCode import add_user, get_repos, delete_repo, add_repo

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
        return render_template("home.html", user_name=user.username, avatar=user.avatar_url, repositories=repositories)

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

        return jsonify({"status": "error"})

# ADD page
@views.route('/add', methods=['GET','POST'])
def add():

    if request.method == 'GET':
        # get the user's name and photo
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        return render_template("add.html", user_name=user.username, avatar=user.avatar_url)
    
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






        