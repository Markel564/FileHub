""" 
This section contains the view for the error page of the website

It is displayed when there is a problem with the authentication of the user

"""

from flask import Blueprint, render_template, request



errorPage = Blueprint('errorPage', __name__)

@errorPage.route('/error', methods=['GET'])
def error():
    if request.method == 'GET':
        return render_template("error.html")
