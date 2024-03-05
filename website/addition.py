from flask import Blueprint, flash, request, jsonify
from .pythonCode import *

addition = Blueprint('addition', __name__)



@addition.route('/upload-file', methods=['GET','POST'])
def upload_file():
    if 'file' in request.files:
        print ("File received")
        file = request.files['file']
        # Save the uploaded file to a directory on the server
        file.save('uploads/' + file.filename)
        # add the file to the database
        path = request.form.get('path')
        
        repoName = request.form.get('repoName')

        repo = Repository.query.filter_by(name=repoName).first()

        if not repo.isCloned:
            flash("The repository is not cloned", category='error')
            return jsonify({'error': 'The repository is not cloned'}), 400
        ack = add_file(repoName, file.filename, path) 
            
        if not ack:
            flash("Error adding file to the database", category='error')
            return jsonify({'error': 'Error adding file to the database'}), 400
        

        flash("File uploaded successfully", category='success')
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'error': 'No file received'}), 400
