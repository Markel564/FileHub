from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .pythonCode import validate_token, add_user
from flask_login import login_user
from .models import User

initialPage = Blueprint('initialPage', __name__)


# initial page

@initialPage.route('/', methods=['GET','POST'])
def create_token():

    if request.method == 'GET':
        
        user = User.query.filter_by(id=session.get('user_id')).first()
        if user:
            print(f"User {user.username} already logged in!")
        return render_template("initial.html")

    elif request.method == 'POST':

        data = request.get_json()  
        
        type_message = data.get('type')

        if type_message == "token":

            token = data.get('token')
            
            valid = validate_token(token)

            if valid:
                session['token'] = token

                ack = add_user()

                if ack != 0:
                    return jsonify({"status": "error"})
                
                user_id = session.get('user_id')
                user = User.query.filter_by(id=user_id).first()
                login_user(user) # login the user
                print(f"User {user.username} logged in!")
                return jsonify({"status": "ok"})
            else:
                flash("User not identified!", category='error')
                return jsonify({"status": "error"})
            
            
