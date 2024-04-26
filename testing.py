import github
from github import Github, Auth
import requests




token = "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"
owner = "MarkelBene"
repo = "MyFirstRepo"

g = github.Github("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")

user = g.get_user()

url = f"https://api.github.com/repos/{owner}/{repo}/contents/"

headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
print (f"MAKING REQUEST with url {url} and headers {headers}")

response = requests.get(url, headers=headers)
print (f"RESPONSE: {response}")

contents = response.json()

print (f"CONTENTS: {contents}")
for content_file in contents:
            
    if content_file['type'] == "file":
        print (f"FILE: {content_file['name']}")
    else:
        print (f"FOLDER: {content_file['name']}")