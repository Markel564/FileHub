"""
This section contains the views of the website

Each view is a function for a specific route

The views are:

    - home: the main page of the website where the user can see his/her repositories
    - add: page that allows the user to add a new repository

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
        print ("GOT REPOS")

        if not repositories:
            print ("Error getting repos")
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

            if ack == 0:
                flash("Project deleted successfully", category='success')
                
            elif ack == 1:
                flash("User not identified!", category='error')
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


        elif type_message == "logout":

            session.pop('user_id', None)
            session.pop('repo_to_remove', None)
            session.pop('token', None)
            session.pop('key', None)
            session.pop('iv', None)
            session.pop('tag', None)
            print ("User logged out")

            db.session.commit()
            logout_user()

            return jsonify({"status": "ok"})


            
            
            






    




    
    
        

    
 
    
    
        
    

        

            