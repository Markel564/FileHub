from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User, Repository
from .pythonCode import get_invitations, handle_invitation
from flask_login import login_required


invitations = Blueprint('invitations', __name__)

@login_required
@invitations.route('/invitations', methods=['GET','POST'])
def view_invitations():

    if request.method == "GET":


        # get the user from the database
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

        invitations = get_invitations()

    
        return render_template("invitations.html", header_name=user.username, avatar=user.avatarUrl, invitations=invitations)


    if request.method == "POST":

        data = request.get_json()  # get the data from the request

        type_message = data.get('type')


        if type_message == "accept":

            repo = data.get('repoName')
            owner = data.get('owner')


            ack = handle_invitation(repo, owner, "accept")
            
            if ack == 0:
                flash("Invitation accepted", "success")
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not found!", "error")
                return jsonify({"status": "usrError"})
            elif ack == 2:
                flash("Error accepting invitation", "error")
                return jsonify({"status": "error"})
            else:
                flash("An unexpected error occurred!", "error")
                return jsonify({"status": "unexpectedError"})

        
        if type_message == "decline":

            repo = data.get('repoName')
            owner = data.get('owner')

            ack = handle_invitation(repo, owner, "decline")

            if ack == 0:
                flash("Invitation declined", "success")
                return jsonify({"status": "ok"})
            elif ack == 1:
                flash("User not found", "error")
                return jsonify({"status": "userError"})
            else:
                flash("Error declining invitation", "error")
                return jsonify({"status": "error"})


