from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User
from .pythonCode import add_repo


additionRepo = Blueprint('additionRepo', __name__)



# ADD page
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

            
            # create the repo
            ack = add_repo(project_name, project_description, readme, isPrivate)
            
            if ack == 0:
                flash("Repository created successfully", category='success')
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not identified!", category='error')
                return jsonify({"status": "errorUser"})
            elif ack == 2:
                flash("There is already a repository with the same name!", category='error')
                return jsonify({"status": "errorRepoAlreadyExists"})
            elif ack == 3:
                flash("There was a Github error!", category='error')
                return jsonify({"status": "githubError"})
            elif ack == 4:
                flash("Error adding repository to the database!", category='error')
                return jsonify({"status": "errorDB"})
            else:
                flash("An unexpected error occurred!", category='error')
                return jsonify({"status": "unexpectedError"})
