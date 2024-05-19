""" 
This section contains the view for the initial page of the website

It is displayed when the user accesses the website for the first time,
and prompts the user to introduce a token to access the website

The token can be obtained from the GitHub account (see the README.md file)

"""

from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .pythonCode import validate_token, add_user
from flask_login import login_user
from .models import User

initialPage = Blueprint('initialPage', __name__)


# initial page

@initialPage.route('/', methods=['GET','POST'])
def create_token(): 

    if request.method == 'GET': # if the user is accessing the website for the first time
        
        return render_template("initial.html")

    elif request.method == 'POST': # if the user is sending the token

        data = request.get_json()  
        type_message = data.get('type')


        if type_message == "token":

            token = data.get('token')
            valid = validate_token(token) # validate the token
     
            if valid: # if the token is valid
                ack = add_user(token) # add the user to the database
                if ack != 0:
                    flash("An unexpected error occurred!", category='error')
                    return jsonify({"status": "error"})
                else:
                    user_id = session.get('user_id')
                    user = User.query.filter_by(id=user_id).first()
                    login_user(user) # login the user     
            else:
                flash("User not identified!", category='error')
                return jsonify({"status": "error"})
                
            return jsonify({"status": "ok"})
            
            
