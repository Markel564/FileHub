
const backButton = document.querySelector("#backButton");
const searchInput = document.querySelector("[data-search");
const filesAndFolders = document.querySelectorAll(".content-box");
var folderName = document.title;
const repoName = document.querySelector("#headerName").textContent;
const addFileButton = document.querySelector("#add-file");
const refreshGitHubButton = document.querySelector("#refresh-github");
const refreshFileSystemButton = document.querySelector("#refresh-filesystem");
const commitButton = document.querySelector("#pushButton");
const newFolderButton = document.querySelector("#new-folder");



// function to go back to one page before
backButton.addEventListener("click", () => {

    fetch("/repo/"+folderName, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: "back" }),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    })
    .then(function (data) {
        if (data.status == "ok"){
            // eliminate the last folder from the path
            var path = window.location.pathname.split("/");
            path.pop();
            path = path.join("/");
            // we add the final "/" to the path
            var count = (path.match(/\//g) || []).length;

            path = path + "/";
            if (path == "/repo/"+folderName+"/"){ // if we are in the root of the repository
                window.location.replace("/home"); 
            }
            // There are two cases:
            // a) The redirection takes you to the root of the repository (path = "/repo/folderName/")
            // b) The redirection takes you to a folder (path = "/repo/folderName/folder")
            // The difference is that in the first case, the path has a final "/", and in the second case, it does not have it
            // count the number of "/" in the path
            else if (count == 2){ // option a
                window.location.replace(path)
            }
            else { // option b
                // eliminate the final "/" from the path
                path = path.substring(0, path.length-1);
                window.location.replace(path);
        }
    }})
    .catch(function (error) {
        console.error("Fetch error:", error);
    });

})



// function to search for a folder or file
searchInput.addEventListener("input", (e) => {

    // Value of input
    const value = e.target.value.toLowerCase();

    filesAndFolders.forEach((element) => {

        // Check if the folder or file name contains the value of the input
        const isVisible = element.querySelector("h1").textContent.toLowerCase().includes(value);

        // If the folder or file name does not contain the value of the input, hide it
        element.classList.toggle("hide", !isVisible);
    });

    // if there are no files or folders, display the div 'no-results'
    const numberOfVisibleFilesAndFolders = document.querySelectorAll(".content-box:not(.hide)").length;
    const noResultsDiv = document.querySelector(".no-results");

    if (numberOfVisibleFilesAndFolders === 0) {
        noResultsDiv.style.display = "flex";
    } else {
        noResultsDiv.style.display = "none";
    }

});


// function to open a folder
document.addEventListener("DOMContentLoaded", function () {
    const folders = document.querySelectorAll("#folder");

    folders.forEach(folder => {
        folder.addEventListener("click", (event) => {
            // Ensure click doesn't propagate when clicking delete button
            if (event.target.classList.contains('delete-folder')) {
                event.stopPropagation();
                return;
            }

            const folderName = folder.querySelector("h1").textContent;

            let Path = window.location.pathname;
            let folderPath = Path.substring(6);

            if (folderPath[folderPath.length-1] != "/") {
                folderPath = folderPath + "/";
            }

            fetch("/repo/"+folderPath, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ type: "open", folder: folderName, folderPath: folderPath }),
            })
            .then(function (response) { 
                if (response.ok) {
                    return response.json(); 
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function (data) {
                let path = data.path;
                if (data.status == "ok"){
                    window.location.replace("/repo/"+path);
                }
            })
            .catch(function (error) {
                console.error("Fetch error:", error);
            });
        });
    });

    var deleteButtons = document.querySelectorAll(".delete-folder");

    deleteButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent propagation to content box click listener

            var folderName = this.closest('#folder').querySelector("h1").textContent;
            
            let path = window.location.pathname;
            path = path.substring(6);
            path = path.substring(repoName.length);
            path = path.substring(1);
            if (path[path.length-1] != "/"){
                path = path + "/";
            }

            fetch("/repo/"+ repoName + "/",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ type: "delete-folder", repoName: repoName, folderPath: path, folderName: folderName}),
            })
            .then(function (response) {
                if (response.ok) {
                    return response.json(); 
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function (data) {
                if (data.status == "ok"){
                    window.location.reload();
                }else{
                    window.location.reload();
                }

            })
            .catch(function (error) {
                console.error("Fetch error:", error);
            });
        });
    });
});



// Drag and drop functionality
let files = [];
Dropzone.autoDiscover = false;
if (!document.querySelector('.dropzone').classList.contains('dz-clickable')) {
    let path = window.location.pathname;
    // remove the initial "/repo/" from the path
    path = path.substring(6);
    // remove the repoName from the path
    path = path.substring(repoName.length);
    // finally, remove the first "/" of the remaining path
    path = path.substring(1);
    // add the final "/" to the path
    if (path[path.length-1] != "/"){
        path = path + "/";
    }
    
    let myDropzone = new Dropzone(".dropzone", {
        url:'/upload-file',
        maxFilesize:104857600, // 100MB (GitHub limit)
        maxFiles:1,
        acceptedFiles: ".*",
        addRemoveLinks:false,
        previewTemplate: '<div class="dz-preview dz-file-preview"></div>',
        sending: function(file, xhr, formData) {
            formData.append("repoName", repoName);
            formData.append("path", path);
        },
    });
    
    myDropzone.on("addedfile", function(file) {
        files.push(file);
    });

    myDropzone.on("removedfile", function(file) {
        let index = files.indexOf(file);
        files.splice(index, 1);
    });

    myDropzone.on("error", function(file, errorMessage) {
        if (errorMessage === "You can't upload files of this type.") {
            alert(errorMessage);
            myDropzone.removeFile(file);
        }
    });

    myDropzone.on("success", function() {
        window.location.reload();
    });

    // even when it is a failure to upload the file, we reload the page
    myDropzone.on("error", function() {
        console.log("ERROR")
        window.location.reload();
    });
}

// prevent small rectangles for dragging files
document.getElementById('add-file').addEventListener('submit', function(event) {
    event.preventDefault(); 
});

// function to upload a file by clicking the add-file div
addFileButton.addEventListener("click", () => {
    document.getElementById('file-input').click(); // Click on the file input
});

// event listener for the file input
document.getElementById('file-input').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file){
        let formData = new FormData();
        formData.append("file", file);
        formData.append("repoName", repoName);
        // similar to before, we construct the path
        let path = window.location.pathname;
        path = path.substring(6);
        path = path.substring(repoName.length);
        path = path.substring(1);
        if (path[path.length-1] != "/"){
            path = path + "/";
        }
        formData.append("path", path);

        fetch("/upload-file", {
            method: "POST",
            body: formData,
        })
        .then(function (response) {
            if (response.ok) {
                return response.json(); 
            } else {
                throw new Error("Network response was not ok");
            }
        })
        .then(function (data) {
            console.log("DATA", data)
            if (data.status == "ok"){
                window.location.reload();
            }
            else{
                window.location.reload();
            }
        }) 
        .catch(function (error) {
            window.location.reload();
            console.error("Fetch error:", error);
        });
    }
});



// function to open the window to clone a repository
document.addEventListener("DOMContentLoaded", function () {

    var synchronizeButton = document.querySelector("#cloneButton");

    synchronizeButton.addEventListener("click", () => {

        fetch("/repo/" + repoName + "/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({type: "clone-request", repoName: repoName}),
        })
        .then(function (response) {
            if (response.ok) {
                return response.json(); 
            } else {
                throw new Error("Network response was not ok");
            }
        })
        .then(function (data) {

            if (data.status == "ok"){

                var errorContainer = document.getElementById("modal-content");
                var state = false; 
                function toggleState() {
                            
                    if (state){ // if state is true, then hide the modal
                        errorContainer.classList.remove("modal-content");
                        errorContainer.classList.add("hide")
                    }else{
                        errorContainer.classList.remove("hide");
                        errorContainer.classList.add("modal-content");
                    }
                }
                        
                toggleState();
            }
            else{
                window.location.reload();
            }
        })
        .catch(function (error) {
            console.error("Fetch error:", error);
        });

    });

});




// function to refresh from the GitHub repository
refreshGitHubButton.addEventListener("click", () => {

    // similar to before, we construct the path, because this
    // time the system is going to update the files from the Github
    // repository from this path onwards
    let Path = window.location.pathname;
    let folderPath = Path.substring(6);   

    if (folderPath[folderPath.length-1] != "/"){
        folderPath = folderPath + "/";
    }
    fetch("/repo/"+repoName + "/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: "refresh-github", folderPath: folderPath, repoName: repoName }),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    })
    .then(function (data) {
        if (data.status == "ok"){
            window.location.reload();
        }

    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
});


// function to refresh from the file system
refreshFileSystemButton.addEventListener("click", () => {

   
    fetch("/repo/"+repoName + "/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: "refresh-filesystem", repoName: repoName }),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    })
    .then(function (data) {
        if (data.status == "ok"){
            window.location.reload();
        }else{
            window.location.reload();
        }

    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
});



// function to commit changes to the repository
pushButton.addEventListener("click", () => {
    let Path = window.location.pathname;
    let folderPath = Path.substring(6);
    if (folderPath[folderPath.length-1] != "/"){
        folderPath = folderPath + "/";
    }


    fetch("/repo/"+repoName + "/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: "commit", repoName: repoName, folderPath: folderPath}),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    })
    .then(function (data) {
        if (data.status == "ok"){
            window.location.reload();
        }else{
            window.location.reload();
        }

    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
});



// function to delete a file
document.addEventListener("DOMContentLoaded", function () {

    var deleteButtons = document.querySelectorAll(".delete-file");

    deleteButtons.forEach(function (button) {
        button.addEventListener("click", function () {

            var fileName = this.closest('#file').getAttribute("name");
            
            let path = window.location.pathname;
            path = path.substring(6);
            path = path.substring(repoName.length);
            path = path.substring(1);
            if (path[path.length-1] != "/"){
                path = path + "/";
            }

            fetch("/repo/"+ repoName + "/",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ type: "delete-file", repoName: repoName, folderPath: path, fileName: fileName}),
            })
            .then(function (response) {
                if (response.ok) {
                    return response.json(); 
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function (data) {
                if (data.status == "ok"){
                    window.location.reload();
                }else{
                    window.location.reload();
                }

            })
            .catch(function (error) {
                console.error("Fetch error:", error);
            });
        });
    }
    );
});


// Function to open window to create folder
newFolderButton.addEventListener("click", () => {

    let path = window.location.pathname;
    path = path.substring(6);
    path = path.substring(repoName.length);
    path = path.substring(1);
    if (path[path.length-1] != "/"){
        path = path + "/";
    }

    fetch("/repo/"+ repoName + "/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: "new-folder-request", repoName: repoName, folderPath: path}),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    })
    .then(function (data) {
        
        var folderWindow = document.getElementById("modal-folder");

        if (data.status == "ok"){
            folderWindow.classList.remove("hide");
            folderWindow.classList.add("modal-folder");
        }
    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
});


// Function to open a file by clicking it
document.addEventListener("DOMContentLoaded", function () {

    var files = document.querySelectorAll("#file");

    files.forEach(function (file) {

        file.addEventListener("click", function () {

            
            var fileName = this.getAttribute("name");
            let path = window.location.pathname;
            path = path.substring(6);
            path = path.substring(repoName.length);
            path = path.substring(1);
            if (path[path.length-1] != "/"){
                path = path + "/";
            }

            fetch("/repo/"+ repoName + "/",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ type: "open-file", repoName: repoName, folderPath: path, fileName: fileName}),
            })
            .then(function (response) {
                if (response.ok) {
                    return response.json(); 
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function (data) {
                if (data.status == "ok"){
                    window.location.reload();
                }else{
                    window.location.reload();
                }
            })
            .catch(function (error) {
                console.error("Fetch error:", error);
            });
        });
    });
});





