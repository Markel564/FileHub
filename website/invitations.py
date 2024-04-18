from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User, Repository
from .pythonCode import get_invitations


invitations = Blueprint('invitations', __name__)


@invitations.route('/invitations', methods=['GET','POST'])
def view_invitations():

    if request.method == "GET":


        # get the user from the database
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()

        print ("GET INVITATIONS")
        invitations = get_invitations()

        return render_template("invitations.html", header_name=user.username, avatar=user.avatarUrl, invitations=invitations)


    if request.method == "POST":

        type_message = request.form.get('type')

        if type_message == "back":

            return jsonify({"status": "ok"})
