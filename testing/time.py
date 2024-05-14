from github import Github, Auth
import github
import requests
import time




# access repository using https
def func1(username, token):
    repositories = []
    
    # Obtain repos
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    start = time.time()
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repos_data = response.json()
        for repo_data in repos_data:
            repository = {
                "name": repo_data["name"],
                "contents": []
            }
            
            # Obtain contents
            contents_url = f"https://api.github.com/repos/{username}/{repo_data['name']}/contents"
            response_contents = requests.get(contents_url, headers=headers)
            if response_contents.status_code == 200:
                contents_data = response_contents.json()
                for content_data in contents_data:
                    repository["contents"].append(content_data["name"])
            
            repositories.append(repository)
    else:
        print("Failed to fetch repositories:", response.status_code)
    
    end = time.time()
    print("Time taken for fun1:", end - start)
    return repositories


# access repository using pygithub
def func2(username, token):
    repositories = []
    

    start = time.time()
    g = Github(token)
    user = g.get_user(username)
    
    for repo in user.get_repos():
        repository = {
            "name": repo.name,
            "contents": []
        }
        
        # get contents
        contents = repo.get_contents("")
        for content_file in contents:
            repository["contents"].append(content_file.name)
        
        repositories.append(repository)
    
    end = time.time()
    print("Time taken for fun2:", end - start)
    return repositories





if __name__ == "__main__":
    
    username = None # username
    token = None # token

    if not username or not token:
        print("Please provide username and token")
    else:
        func1(username, token)
        func2(username, token)











