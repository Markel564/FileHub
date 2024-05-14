from github import Github, Auth
import github
import requests




# access repository using https
def func1(repo, token, owner):
    print("func1")
    g = github.Github(token)
    user = g.get_user()


    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)

        contents = response.json()

        if response.status_code == 200:

            print ("Func1 success")
        else:
            print ("Func1 failed")
    except Exception:
        print ("Func1 failed")
        


# access repository using pygithub
def func2(repo, token, owner):
    print("func2")
    g = github.Github(token)
    user = g.get_user()
    repositories = user.get_repos()

    
    try:
        repo = g.get_repo(f"{owner}/{repo}")

        contents = repo.get_contents("")
        print ("Func2 success")
    except Exception:
        print ("Func2 failed")




if __name__ == "__main__":
    
    repo = None # name of repository which you are collaborating
    token = None # token of the user who is collaborating
    owner = None # owner of the repository
    func1(repo, token, owner)
    func2(repo, token, owner)











