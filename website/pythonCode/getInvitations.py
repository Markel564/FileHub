from ..models import User
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
import os
from sqlalchemy.exc import SQLAlchemyError
from .reformatDate import change_format_date



def get_invitations():
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return 1

    try:
        g = Github(user.githubG)
        user = g.get_user()

        invitations = user.get_invitations()

        print (f"User name: {user.name}, user email: {user.email}")
        invites = {}
        for invitation in invitations:
            # print the repository name, the date and the user who sent the invitation
            invites['inviter'] = invitation.inviter.login
            invites['repository'] = invitation.repository.name
            invites['date'] = change_format_date(invitation.created_at)
            invites['avatar'] = invitation.inviter.avatar_url

        return invites
    except Exception as e:
        print(e)
        return 2
