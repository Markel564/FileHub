// const Dropzone = require("dropzone");

const backButton = document.querySelector("#backButton");
const searchInput = document.querySelector("[data-search");
const filesAndFolders = document.querySelectorAll(".content-box");
var folderName = document.title;
const repoName = document.querySelector("#headerName").textContent;
const folders = document.querySelectorAll("#folder");
const addFileButton = document.querySelector("#add-file");

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
                window.location.replace("/"); 
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
                // window.location.replace("/repo/"+path);
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
folders.forEach(folder => {
    
    folder.addEventListener("click", () => {
        const folderName = folder.querySelector("h1").textContent;
        
        let Path = window.location.pathname;
        // eliminate "/repo/" from the folder path which is the first 6 characters
        let folderPath = Path.substring(6);
        
        
        // since the location of the folder does have a final "/", if there is not a final "/", we add it
        if (folderPath[folderPath.length-1] != "/"){
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
        acceptedFiles: ".docx",
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

    myDropzone.on("success", function(file, response) {
        console.log("Success")
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
                // we reload the page
                console.log("RELOAD")
                window.location.reload();
            }
        }) 
        .catch(function (error) {
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
            body: JSON.stringify({type: "clone-request", repoName: repoName }),
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
        })
        .catch(function (error) {
            console.error("Fetch error:", error);
        });

    });
}); 