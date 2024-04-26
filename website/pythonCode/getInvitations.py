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

        invites = []
        for invitation in invitations:
            
            invites.append({
                'inviter': invitation.inviter.login,
                'repository': invitation.repository.name,
                'date': change_format_date(invitation.created_at),
                'avatar': invitation.inviter.avatar_url
            })

        return invites
    except Exception as e:
        print(e)
        return 2
