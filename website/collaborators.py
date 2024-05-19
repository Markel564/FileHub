""" 
This section contains the view for the collaborators page of the website

It is used whenever the user accesses the collaborators page of a repository

"""

from flask import Blueprint, render_template, flash, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Repository
from .pythonCode import get_collaborators, eliminate_collaborator, add_collaborator
from flask_login import login_required


collabPage = Blueprint('collabPage', __name__)


# COLLABORATORS PAGE
@login_required
@collabPage.route('/<repoName>/collaborators', methods=['GET', 'POST'])
def collaboration(repoName):

        if request.method == 'GET':
            
            # get the user from the database
            user_id = session.get('user_id')
            user = User.query.filter_by(id=user_id).first()

            collaborators = get_collaborators(repoName) # get the collaborators of the repository

            if collaborators == 1 or collaborators == 2 or collaborators == 3:
                # redirect to repository page
                flash("Error getting collaborators", "error")
                return redirect(url_for('repository.repo', subpath=repoName+"/"))
            
            # render the collaborators page
            return render_template("collaborators.html", header_name=repoName, avatar=user.avatarUrl, collaborations=collaborators)

        else: # things that the user can do inside the collaborators page
            
            data = request.get_json()  
        
            if data is None: # if no data was sent
                return jsonify({"status": "error"})

            type_message = data.get('type') # get the type of message

            if type_message == "remove": # if the user wants to remove a collaborator
                
                # get the repo name and the collaborator name
                repoName = data.get('repoName')
                collaboration = data.get('collaboratorName')

                user_id = session.get('user_id')
                user = User.query.filter_by(id=user_id).first()
                
                if user.username == collaboration: # if the user is trying to remove himself
                    flash("You can't remove yourself from the collaborators list", "error")
                    return jsonify({"status": "error"})
                
                ack = eliminate_collaborator(repoName, collaboration) # remove the collaborator

                if ack == 0: 
                    flash("Collaborator removed", "success")
                elif ack == 1:
                    flash("User not found", "error")
                    return jsonify({"status": "error"})
                elif ack == 2:
                    flash("You can't remove the owner of the repository", "error")
                else:
                    flash("Error removing collaborator", "error")

                return jsonify({"status": "ok"})
            
            elif type_message == "add": # if the user wants to add a collaborator
                    
                # get the data from the POST request
                repoName, collaboration, isAdmin, isWriter, isReader = data.get('repoName'), data.get('collaboratorName'), data.get('admin'), data.get('writer'), data.get('reader')
                
                ack = add_collaborator(repoName, collaboration, isAdmin, isWriter, isReader) # add the collaborator

                if ack == 0:
                    flash ("Collaborator invited", "success")
                elif ack == 1:
                    return jsonify({"status": "error"})
                elif ack == 2:
                    flash ("No role was selected", "error")
                elif ack == 3:
                    flash ("You can't add yourself as a collaborator", "error")
                elif ack == 4:
                    flash ("Please select only 1 role", "error")
                elif ack == 5:
                    flash ("Collaborator already exists", "error")
                else:
                    flash ("Error inviting collaborator", "error")
                
                return jsonify({"status": "ok"})
                