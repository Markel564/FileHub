## Contributions

The 'killer' of this app is the efficiency:
<br>

When a file/folder loads (see load_files_and_folders.py) from Github, the API
gives the following info about such document:


- name: name of document
- path: relative path within file
- sha: hash value (SHA-1) of document
- size: size of document in bytes
- url: URL for direct access
- html_url: URL in web
- git_url; URL that points to the documents' Git Object
- download_url: URL for downloading the document
- type: file/folder
- links: additional links

Hence, it is missing a crutial element; the last_modified date of file. Initially,
the library PyGithub was used, but apparently there are some problems with it:

- https://github.com/PyGithub/PyGithub/issues/629
- https://github.com/PyGithub/PyGithub/pull/1032

Apparently, there are some errors with it, and the last_modified attribute corresponds
to the last modification of the whole repository.

The temporary approach adopted involves making an extra API call for each document to see
the repositories last commit regarding this file/folder, which in turn, is quite expensive efficiency-wise.
Also, to compare with the last modified attribute previously, a series of conversion (to get rid of 
timezones) have to be performed, which also delay slightly the response time. 

Hence, this is the <strong> most important contribution </strong> yet to make; a way of solving this
issue up until PyGithub fixes it.

Other than that, the following can be added:
- Make the app more responsive
- Check for more errors
- Usability studies
- More funcions added, like the incorporation of branches
- A message system between collaborators

Thank you so much! Feel free to email me at
100451267@alumnos.uc3m.es or markelbenedicto@gmail.com
for any suggestions or questions!


