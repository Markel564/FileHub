from github import Github, Auth
import github
from datetime import datetime
import pytz
from tzlocal import get_localzone
import time
from cachetools import TTLCache
import os
from sqlalchemy.exc import SQLAlchemyError
import requests
from datetime import datetime, timedelta




repo = "TestingClone"
token = "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"
owner = "Markel564"


def func(repo, token, owner):

    g = github.Github(token)
    user = g.get_user()


    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    contents = response.json()

   
    start = time.time()
    for content in contents:
        # print the last modified time of the file
        print (content.keys())

    print ("Time taken: ", time.time()-start)




if __name__ == "__main__":
    func(repo, token, owner)