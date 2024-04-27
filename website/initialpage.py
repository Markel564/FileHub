from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .pythonCode import validate_token

initialPage = Blueprint('initialPage', __name__)


# initial page

@initialPage.route('/', methods=['GET','POST'])
def create_token():

    if request.method == 'GET':
        
        return render_template("initial.html")

    elif request.method == 'POST':

        data = request.get_json()  
        
        type_message = data.get('type')

        if type_message == "token":

            token = data.get('token')
            
            valid = validate_token(token)

            if valid:
                session['token'] = token
                return jsonify({"status": "ok"})
            else:
                flash("User not identified!", category='error')
                return jsonify({"status": "error"})
            
            
