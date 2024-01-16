from flask import Blueprint, render_template, flash, request, jsonify, session
from . import db
from .models import User
import yaml
views = Blueprint('views', __name__)
from github import Github


@views.route('/', methods=['GET','POST'])
def home():

    add_user()
    
    # get the user from the database
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    
    # get the user's repositories
    repositories = get_repos()
    return render_template("home.html", user_name=user.username, avatar=user.avatar_url, repositories=repositories)





def add_user():
    with open("config.yml", 'r') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)

    g = Github(conf['api_token'])
    

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
        # flash(f'Account created for {name}!', category='success')
    else:
        print (f"Account already exists for {name}")
        # flash(f'Account already exists for {name}!', category='success')

    get_repos()
    print (f"Authenticated as {user.login}")



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
    
    return repositories