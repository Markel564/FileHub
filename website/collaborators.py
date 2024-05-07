from flask import Blueprint, render_template, flash, request, jsonify, session
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
            
            user_id = session.get('user_id')
            user = User.query.filter_by(id=user_id).first()

            collaborators = get_collaborators(repoName)

            if collaborators == 1 or collaborators == 2:
                return render_template("error.html")

            return render_template("collaborators.html", header_name=repoName, avatar=user.avatarUrl, collaborations=collaborators)

        else:
            
            data = request.get_json()  
        
            if data is None: # if no data was sent
                return jsonify({"status": "error"})

            type_message = data.get('type')

            if type_message == "remove":

                repoName = data.get('repoName')
                collaboration = data.get('collaboratorName')

                user_id = session.get('user_id')
                user = User.query.filter_by(id=user_id).first()
                
                if user.username == collaboration:
                    flash("You can't remove yourself from the collaborators list", "error")
                    return jsonify({"status": "error"})
                
                ack = eliminate_collaborator(repoName, collaboration)

                if ack == 0:
                    flash("Collaborator removed", "success")
                elif ack == 1:
                    flash("User not found", "error")
                elif ack == 2:
                    flash("You can't remove the owner of the repository", "error")
                else:
                    flash("Error removing collaborator", "error")

                return jsonify({"status": "ok"})
            
            elif type_message == "add":

                repoName, collaboration, isAdmin, isWriter, isReader = data.get('repoName'), data.get('collaboratorName'), data.get('admin'), data.get('writer'), data.get('reader')
                
                ack = add_collaborator(repoName, collaboration, isAdmin, isWriter, isReader)

                if ack == 0:
                    flash ("Collaborator invited", "success")
                elif ack == 1:
                    flash ("User not found", "error")
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
                