from flask import Blueprint, render_template, flash, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Repository
import yaml
views = Blueprint('views', __name__)
from github import Github


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
        
        repo_name = data.get('repo_name')
        type_message = data.get('type')


        if type_message == "eliminate":
            
            session['repo_to_remove'] = repo_name
            # LUEGO DE ELIMINAR EL REPO, QUITARLO DE LA BASE DE DATOS
            return render_template('delete-info.html') 

        elif type_message == "eliminate-confirm":
            return render_template("error.html")

        elif type_message == "eliminate-cancel":
            return render_template("error.html")
            
        return render_template("generic_error.html")


def add_user():
    with open("config.yml", 'r') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)

    try:
        g = Github(conf['api_token'])
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