from flask import Blueprint, render_template, flash, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Repository
import yaml
views = Blueprint('views', __name__)
from github import Github
from github import Auth
from git import Repo
import github
import os


@views.route('/', methods=['GET','POST'])
def home():

    if request.method == 'GET':

        if not add_user():  # error with the api token
            return render_template("error.html")

        
        # get the user from the database
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        
        # get the user's repositories
        repositories = get_repos()
        


        return render_template("home.html", user_name=user.username, avatar=user.avatar_url, repositories=repositories)

    if request.method == 'POST':

        data = request.get_json()  # Get JSON data from the request
        
        if data is None:
            return render_template("generic_error.html")
        
        type_message = data.get('type')


        if type_message == "eliminate":

            repo_name = data.get('repo_name')
            session['repo_to_remove'] = repo_name
            # LUEGO DE ELIMINAR EL REPO, QUITARLO DE LA BASE DE DATOS
            return jsonify({"status": "ok"})

        elif type_message == "eliminate-confirm":

            
            ack = delete_repo()

            if ack:
                return jsonify({"status": "ok"})
            
            return jsonify({"status": "error"})

        elif type_message == "eliminate-cancel":
              
            return jsonify({"status": "ok"})

        elif type_message =="add":
            return jsonify({"status": "ok"})


            
        return jsonify({"status": "error"})

@views.route('/add', methods=['GET','POST'])
def add():

    if request.method == 'GET':
        # get the user's name and photo
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        return render_template("add.html", user_name=user.username, avatar=user.avatar_url)
    
    else: # POST
        

        data = request.get_json()  

        if data is None:
            return render_template("generic_error.html")
        
        type_message = data.get('type')

        if type_message == "back":
            return jsonify({"status": "ok"})

        elif type_message == "create":
            
            print ("CREATING REPO")
            
            
            project_name = data.get('projectName')
            project_description = data.get('projectDescription')

            path = data.get('path') 

            isPrivate = data.get('private')
            isReadme = data.get('readme')

            # check if there are no other repos with the same name
            repo = Repository.query.filter_by(name=project_name).first()
            if repo is not None:
                print ("duplicate")
                return jsonify({"status": "errorDuplicate"})
            
            # check if the path is valid
            if not os.path.isdir(path):
                print ("invalid path")
                return jsonify({"status": "errorPath"})
            
            



            return jsonify({"status": "ok"})






def add_user():
    with open("config.yml", 'r') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)

    try:
        auth = Auth.Token(conf['api_token'])
        g = Github(auth=auth, base_url="https://api.github.com")

    except:
        return False

    id = g.get_user().id
    session['user_id'] = id
    user = g.get_user()
    
    name = user.name
    username = user.login
    email = user.email
    avatar = user.avatar_url

    if not User.query.filter_by(id=id).first():
        print (f"Creating account for {name}")
        new_user = User(id=id, g=conf['api_token'], name=name, username=username, email=email, avatar_url=avatar)
        db.session.add(new_user)
        db.session.commit()
        get_repos()

    else:
        print (f"Account already exists for {name}")


    print (f"Authenticated as {user.login}")

    return True


def get_repos():
    """
    Get all the repos of the authenticated user

    returns a list with the names of the repos
    """
    # obtain the user from the database
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    g = Github(user.g)

    

    user = g.get_user()
    repos = user.get_repos()

    repositories = []
    for repo in repos:
        repositories.append(repo.name)

    # add the repositories to the db
    for repo in repositories:
        if not Repository.query.filter_by(name=repo).first():
            print (f"ADDED --> {repo}")
            new_repo = Repository(name=repo, user_id=user_id)
            db.session.add(new_repo)
            db.session.commit()
    
    return repositories


def delete_repo():
    """
    Delete the repo from the github account and from the database
    """

    # obtain the user from the database
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return False

    try:
        g = github.Github(user.g)
        user = g.get_user()

        repo_name = session.get('repo_to_remove')
        # search for the repo in the database
        repo = Repository.query.filter_by(name=repo_name).first()
        if repo is None:
            return False


        repo = user.get_repo(repo_name)
        repo.delete()

        # delete the repo from the database
        repo = Repository.query.filter_by(name=repo_name).first()
        db.session.delete(repo)
        db.session.commit()

        session['repo_to_remove'] = None

        return True
    except github.GithubException as e:
        return False