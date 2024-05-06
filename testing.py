import requests

# Define the repository details and token
owner = "Markel564"
repo = "TestingClone"
token = "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"

# URL for the list of collaborators in the repository
url = f"https://api.github.com/repos/{owner}/{repo}/collaborators"


# Headers with the authorization token
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

print(f"URL is {url} with headers {headers}")
# Make the request to the GitHub API
response = requests.get(url, headers=headers)

print(f"Response is {response}")
collaborators = response.json()

for collaborator in collaborators:
    print(collaborator)
    print ("\n")
    
