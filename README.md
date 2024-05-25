
# FileHub

Welcome to FileHub, an app created to avoid using Git commands to publish
your work to GitHub

This web service is designed for unexperienced users who aim to submit their
files to GitHub and therefore synchronize their local filesystem GitHub. In
a way, it is like allowing certain basic features such as

```bash
  git clone <repository>
  git pull
  git push 
```

as well as otherslike inviting/deleting collaborators and accepting invitations

To add to this, just comment that this readme file plus the screenshots folder has 
been added to this repository using FileHub

## Obtaining a Personal Token

Use the following 
[link](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens "Title")

to generate a Personal Access Token (PAT). The following must be used to 
use the apps full functionality:

- classic token 
- attribute repo
- attribute user
- attribute delete_repo


Keep the token generated saved and use it in the initial page displayed!

The following personal data will be used by the application:

- User's username & avatar
- User's timezone 
- Any github objects associated with the PAT


## Installation

To install this project, firstly, get the needed dependencies

```bash
  pip install -r requirements.txt
```
    
## Deployment

To deploy, change the secret key in line 15 of the __init__.py file inside website. Afterwards,
run

```bash
  python3 main.py
```

and open a web browser. The app will be running in <strong>http://localhost:5000/</strong>

## Using FileHub


The first page that will pop up after running python3 main.py will be as 
follows:

<br>
<p align="center">
 <img src="https://github.com/Markel564/readme/blob/main/screenshots/initialPage.png" width="500" style="height: auto;">
</p>

<br>

After you place your PAT, a homepage such as this should pop up:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/mainPage.png" width=500" style="height: auto;">
</p>
<br>


In this page, you can perform the following actions:

- Add a new repository
- View collaboration invitations to other repositories
- Access a repository
- Logout

<br>

If you click 'ADD NEW PROJECT', you will be redirected here:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/addRepoPage.png" width=500" style="height: auto;">
</p>
<br>



There, you can add a new repository, give it a description, an optional absolute path
to clone it to your filesystem and make it private optionally.If you want to
create such repository, click 'CREATE' and it will be added to your repositories (both in the
app and in GitHub).In case you would not like to, just click 'BACK' and will return to the homepage.

Back in the homepage, if you want to delete any repository, just click the trash icon next to it. 

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/trashIcon.png" width=400" style="height: auto;">
</p>
<br>


A confirmation window will pop up asking you if you want to perform that action: 

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/confirmation.png" width=400" style="height: auto;">
</p>
<br>

If you want to see your invitations, click 'VIEW INVITATIONS', and your invitations will show up!

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/invitationsPage.png" width=500" style="height: auto;">
</p>
<br>



There, you can either accept it or decline invitations, if any.

Back in the homepage, to log out, just click the 'LOGOUT' page and it will take you to the initial page. 

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/logout.png" width=200" style="height: auto;">
</p>
<br>

However, lets suppose you want to see a bit more of any repository and actually use the app. In the homepage, just select
and repository. In this example, we will select the repository 'Experimentation'.

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/searchRepo.png" width=400" style="height: auto;">
</p>
<br>

The following page will load, showcasing the contents of the repository you accessed:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/repoPage.png" width=500" style="height: auto;">
</p>
<br>


In this page, you can perform a variety of actions:

- Pull from GitHub
- Push to GitHub
- Clone the repository
- Add a file from the interface
- Add a folder from the interface
- Delete any file or folder
- Access folders
- Update the interface based on the cloned repository
- Add/remove collaborators

If you want to clone the repository in your filesystem, just click the button 'DOWNLOAD'
and the following window will pop up:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/cloneRepo.png" width=400" style="height: auto;">
</p>
<br>


There, enter the windows/unix file system path were you want to clone the repository and click 'OK'. An example of a path can 
be: 

- C:\Users\userName\Folder1\Folder2 (windows format)
- /mnt/c/Users/userName/Folder1/Folder2 (linux format)

Once the repository is cloned, you will see that in that particular location of your filesystem,
a folder representing the repository has been created. There, go on and modify/add/eliminate/rename 
any file you want. If you want to see the changes in the app, click the following button:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/changes.png" width=200" style="height: auto;">
</p>
<br>


You will see the state of your local repository correctly represented, whether that is a new or modified file (in colour green),
or a file that has been deleted (no longer represented). The same applies for folders within the local filesystem. In this example, we added a file called 'new.txt':

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/newFile.png" width=500" style="height: auto;">
</p>
<br>


However, you can add also add a new file or folder from the app directly! Do this by placing a file or clicking the Drag n Drop at the tail end of the repository contents:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/dragndrop.png" width=200" style="height: auto;">
</p>
<br>


You can also add a new folder by clicking the following:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/newFolder.png" width=200" style="height: auto;">
</p>
<br>


This will open up a window to write the name of the folder:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/newFolderWindow.png" width=400" style="height: auto;">
</p>
<br>

If you however, want to delete any file/folder directly from the interface, just click the trash-bin icon appended to the file/folder:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/deleteFile.png" width=200" style="height: auto;">
</p>
<br>


Okay, so, lets say you have created a new folder and want to access the contents of it. Well, for this, just click the folder you want to
access, in my case, 'FirstFolder':

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/firstFolder.png" width=200" style="height: auto;">
</p>
<br>

This will take you to folder were you can see the contents of it displayed.

Okay, let's go back to the basics. If you are willing to push the contents from your local repository to GitHub, click the button
'UPLOAD TO GITHUB':

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/push.png" width=200" style="height: auto;">
</p>
<br>

If that is not the case and instead, you want to do a pull, just click the button with the GitHub icon:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/pull.png" width=200" style="height: auto;">
</p>
<br>

Finally, to add/remove collaborators, click the button 'SHARE'

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/share.png" width=200" style="height: auto;">
</p>
<br>

A page with the collaborators will pop up:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/collabPage.png" width=500" style="height: auto;">
</p>
<br>


Here, to remove someone (this actions will only be allowed if you have the permissions to do so), just click the trash-icon next to 
the collaborator. To add one, click the 'ADD' button and you will be asked to fill some details:

<br>
<p align="center">
  <img src="https://github.com/Markel564/readme/blob/main/screenshots/addCollab.png" width=400" style="height: auto;">
</p>
<br>


Fill the details and a new collaborator will be invited!

That's everything, I hope you enjoy FileHub!!

## Limitations
- efficiency
- screen size 
- etc



## Contributing

Contributions are always welcome!

See `contributing.md` for ways to get started.

Please adhere to this project's `code of conduct`.


## Authors

- [@Markel564](https://www.github.com/Markel564)

