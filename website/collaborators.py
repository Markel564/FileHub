from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User, Repository
from .pythonCode import get_collaborators, eliminate_collaborator
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
            
            print ("POST")
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
                else:
                    flash("Error removing collaborator", "error")

                return jsonify({"status": "ok"})