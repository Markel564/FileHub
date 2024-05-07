from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User
from .pythonCode import add_repo, clone_repo
from flask_login import login_required

additionRepo = Blueprint('additionRepo', __name__)



# ADD page
@login_required
@additionRepo.route('/add', methods=['GET','POST'])
def add():

    if request.method == 'GET':
        # get the user's name and photo
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        return render_template("add.html", header_name=user.username, avatar=user.avatarUrl)
    
    else: # POST
        
        data = request.get_json()  

        if data is None:
            flash("An unexpected error occurred!", category='error')
            return jsonify({"status": "error"})
        
        type_message = data.get('type')

        if type_message == "back":

            # js handles the redirection to /
            return jsonify({"status": "ok"})

        elif type_message == "create":
            
            # get the data from the POST request
            project_name = data.get('projectName')
            project_description = data.get('projectDescription')
            isPrivate = data.get('private')
            pathOfRepo = data.get('repoPath')

            print(project_name, project_description, isPrivate, pathOfRepo)
            # create the repo
            ack = add_repo(project_name, project_description, isPrivate)
            
            if ack == 0:
                
                if pathOfRepo != None:
                    ack = clone_repo(project_name, pathOfRepo)
                    
                    if ack == 0:
                        flash("Project created successfully", category='success')
                    else:
                        flash("Project created successfully, but unable to download the Project", category='error')
                else:
                    flash("Project created successfully", category='success')
            elif ack == 1:
                flash("User not identified!", category='error')
            elif ack == 2:
                flash("There is already a project with the same name!", category='error')
            else:
                flash("Unable to create project", category='error')

            return jsonify({"status": "ok"})
    
