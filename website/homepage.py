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


homePage = Blueprint('homePage', __name__)



# HOME PAGE
@homePage.route('/home', methods=['GET','POST'])
def home():

    if request.method == 'GET':
        
        ack = add_user()

        if ack == 0: # user added successfully
            pass
        elif ack == 1: # user not identified
            flash("User not identified!", category='error')
        elif ack == 2: # error with database
            flash("Error identifying user!", category='error')
        elif ack == 3:
            flash("Error loading projects from GitHub", category='error')
        else:
            flash("An unexpected error occurred!", category='error')
             
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

            if ack == 0:
                flash("Project deleted successfully", category='success')
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("The Project does not exist!", category='error')
                return jsonify({"status": "errorRepoDoesNotExist"})
            elif ack == 3 or ack == 4:
                flash("Error deleting Project!", category='error')
                return jsonify({"status": "errorDB"})
            elif ack == 5:
                flash("You do not own the Project!", category='error')
                return jsonify({"status": "errorRepoNotOwned"})
            elif ack == 6:
                flash("Unable to delete the Project from the file system", category='error')
                return jsonify({"status": "errorFileSystem"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})


        elif type_message == "eliminate-cancel":
            
            # js handles cancelation (just eliminates the pop screen)
            return jsonify({"status": "ok"})
        
        elif type_message == "invitations":

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



            
            
            






    




    
    
        

    
 
    
    
        
    

        

            