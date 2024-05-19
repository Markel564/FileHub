"""
This section contains the views for the home page of the website

it is displayed when the user logs in and it displays the user's repositories
"""

from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User, Repository
from .pythonCode import add_user, get_repos, delete_repo
from flask_login import login_required, logout_user
import os


homePage = Blueprint('homePage', __name__)



# HOME PAGE
@login_required
@homePage.route('/home', methods=['GET','POST'])
def home():

    if request.method == 'GET':
             
        # get the user from the database
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

        # get the user's repositories
        repositories = get_repos()

        if not repositories:
            return render_template("error.html") # if there are no repositories, redirect to the error page
        
        # render template with the user's name, photo and repositories
        return render_template("home.html", header_name=user.username, avatar=user.avatarUrl, repositories=repositories)

    if request.method == 'POST': # things that the user can do inside the home page

        data = request.get_json()  # Get JSON data from the request (done through js)
        
        if data is None: # if no data was sent
            return jsonify({"status": "error"})
        
        type_message = data.get('type')


        if type_message == "eliminate": # if the user wants to delete a repository
             
            # we save the repo name to delete it later
            repo_name = data.get('repo_name') 
            session['repo_to_remove'] = repo_name

            return jsonify({"status": "ok"}) # return ok to js. It will show a modal to confirm the deletion

        elif type_message == "eliminate-confirm": # if the user confirms the deletion of the repository

            # delete the repository
            ack = delete_repo()

            if ack == 0:
                flash("Project deleted successfully", category='success')
                
            elif ack == 1:
                return jsonify({"status": "error"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
            elif ack == 3 or ack == 4:
                flash("Error deleting Project!", category='error')
            elif ack == 5:
                flash("You do not own the Project!", category='error')
            elif ack == 6:
                flash("Unable to delete the Project from the file system", category='error')
            else:
                flash("An unexpected error occurred!", category='error')

            return jsonify({"status": "ok"})


        elif type_message == "logout": # if the user wants to log out

            session.pop('user_id', None)
            session.pop('repo_to_remove', None)
            session.pop('token', None)
            session.pop('key', None)
            session.pop('iv', None)
            session.pop('tag', None)

            db.session.commit()
            logout_user()

            return jsonify({"status": "ok"})


            
            
            






    




    
    
        

    
 
    
    
        
    

        

            