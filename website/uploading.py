from flask import Blueprint, flash, request, jsonify
from .pythonCode import add_file
from flask_login import login_required
import os


uploading = Blueprint('uploading', __name__)


@login_required
@uploading.route('/upload-file', methods=['GET','POST'])
def upload_file():

    if 'file' in request.files:

        file = request.files['file']
        # Save the uploaded file to a directory on the server
        file.save('uploads/' + file.filename)
        # add the file to the database
        path = request.form.get('path')
        
        repoName = request.form.get('repoName')

        ack = add_file(repoName, file.filename, path) 

        print ("REceived ack: ", ack)
        if ack == 0:
            flash ("File uploaded successfully", category='success')
        elif ack == 1:
            flash ("User not identified!", category='error')
        elif ack == 2:
            flash ("The Project does not exist!", category='error')
        elif ack == 3:
            flash ("The Project is not downloaded!", category='error') 
        elif ack == 4:
            flash ("Error finding file!", category='error')
        elif ack == 5:
            flash ("No permissions to add file!", category='error')
        elif ack == 7:
            flash ("That file already exists in the project!", category='error')
        else:
            flash ("An unexpected error occurred!", category='error')
        
        # delete the file from the uploads folder
        os.remove('uploads/' + file.filename)
        return jsonify({'status': 'ok'})

    else:

        flash ("An unexpected error occurred!", category='error')
        return jsonify({'status': 'ok'})
