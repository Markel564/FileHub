from ..models import User
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
import os
from .reformatDate import change_format_date
from .getToken import get_token




def get_invitations():
    token = get_token()

    if not token:
        return 1

    try:
        g = Github(token)
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
        return 2
