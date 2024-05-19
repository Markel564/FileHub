""" 
This section contains the view for the invitations page of the website

It is displayed when the user accesses the invitations page of the website through
the home page

"""

from flask import Blueprint, render_template, flash, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Repository
from .pythonCode import get_invitations, handle_invitation
from flask_login import login_required


invitations = Blueprint('invitations', __name__)

@login_required
@invitations.route('/invitations', methods=['GET','POST'])
def view_invitations():

    if request.method == "GET": # if the user is accessing the invitations page


        # get the user from the database
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

        invitations = get_invitations() # get the invitations of the user

        if invitations == 1 or invitations == 2:
            flash("Error getting invitations", "error")
            return redirect(url_for('homepage.home'))

    
        return render_template("invitations.html", header_name=user.username, avatar=user.avatarUrl, invitations=invitations)


    if request.method == "POST": # things that the user can do inside the invitations page

        data = request.get_json()  # get the data from the request

        type_message = data.get('type')


        if type_message == "accept": # accept an invitation

            repo = data.get('repoName')
            owner = data.get('owner')


            ack = handle_invitation(repo, owner, "accept") # accept the invitation
            
            if ack == 0:
                flash("Invitation accepted", "success")
            elif ack == 1:
                return jsonify({"status": "error"})
            else:
                flash("An unexpected error occurred!", "error")

            return jsonify({"status": "ok"})
        
        if type_message == "decline": # decline an invitation

            repo = data.get('repoName')
            owner = data.get('owner')

            ack = handle_invitation(repo, owner, "decline") # decline the invitation

            if ack == 0:
                flash("Invitation declined", "success")              
            elif ack == 1:
                flash("User not found", "error")
            else:
                flash("Error declining invitation", "error")

            return jsonify({"status": "ok"})


