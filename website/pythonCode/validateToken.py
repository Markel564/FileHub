""" 
This module contains a function that validates a token

It is used to validate the token that the user has entered in the login page

"""
import requests


def validate_token(token: str):
    """ 
    input:
        - token: the token to be validated
    output:
        - True if the token is valid, False otherwise
    """

    try:
        # authenticate the user

        url = "https://api.github.com/user" # url to get the user

        headers = { # headers with the authorization token
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers) # make the request to the GitHub API
        if response.status_code != 200: # if the request was not successful, return False
            return False
        return True # if the request was successful, return True

    except Exception: # if an error occurred, return False
        return False