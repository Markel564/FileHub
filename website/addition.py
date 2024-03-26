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

        repo = Repository.query.filter_by(name=repoName).first()

        ack = add_file(repoName, file.filename, path) 

        if ack == 0:
            flash ("File uploaded successfully", category='success')
            print ("File uploaded successfully")
            return jsonify({'status': 'ok'})
        if ack == 1:
            flash ("User not identified!", category='error')
            return jsonify({'error': 'User not identified'}) 
        elif ack == 2:
            flash ("The repository is not cloned!", category='error') 
            return jsonify({'error', 'The repository is not cloned'})
        elif ack == 3:
            flash ("Error finding file!", category='error')
            return jsonify({'error', 'Error finding file'})
        elif ack == 4:
            flash ("No permissions to add file!", category='error')
            return jsonify({'error', 'No permissions to add file'})
        elif ack == 5:
            flash ("Error adding file to the database!", category='error')
            return jsonify({'error', 'Error adding file to the database'})
        else:
            flash ("An unexpected error occurred!", category='error')
            return jsonify({'error', 'An unexpected error occurred!'})
            

    else:
        flash ("An unexpected error occurred!", category='error')
        return jsonify({'error', 'An unexpected error occurred!'})
