from flask import Blueprint, flash, request, jsonify
from .pythonCode import *

addition = Blueprint('addition', __name__)



@addition.route('/upload-file', methods=['GET','POST'])
def upload_file():
    if 'file' in request.files:

        file = request.files['file']
        # Save the uploaded file to a directory on the server
        file.save('uploads/' + file.filename)
        # add the file to the database
        path = request.form.get('path')
        
        repoName = request.form.get('repoName')

        ack = add_file(repoName, file.filename, path) 

        if ack == 0:
            flash ("File uploaded successfully", category='success')
            return jsonify({'status': 'ok'})
        if ack == 1:
            flash ("User not identified!", category='error')
            return jsonify({'status': 'errorUser'})
        elif ack == 2:
            flash ("The repository does not exist!", category='error')
            return jsonify({'status': 'errorRepoDoesNotExist'})
        elif ack == 3:
            flash ("The repository is not cloned!", category='error') 
            return jsonify({'status': 'errorRepoNotCloned'})
        elif ack == 4:
            flash ("Error finding file!", category='error')
            return jsonify({'status': 'fileError'})
        elif ack == 5:
            flash ("No permissions to add file!", category='error')
            return jsonify({'status': 'permissionError'})
        elif ack == 6:
            flash ("Error adding file to the database!", category='error')
            return jsonify({'status': 'errorDB'})
        elif ack == 7:
            flash ("That file already exists in the repository!", category='error')
            return jsonify({'status': 'errorFileAlreadyExists'})
        else:
            flash ("An unexpected error occurred!", category='error')
            return jsonify({'status': 'unexpectedError'})
            

    else:
        flash ("An unexpected error occurred!", category='error')
        return jsonify({'error', 'An unexpected error occurred!'})
