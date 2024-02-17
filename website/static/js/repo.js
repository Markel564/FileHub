// const Dropzone = require("dropzone");

const backButton = document.querySelector("#backButton");
const searchInput = document.querySelector("[data-search");
const filesAndFolders = document.querySelectorAll(".content-box");
var repoName = document.title;
const folders = document.querySelectorAll("#folder");


// function to go back to one page before
backButton.addEventListener("click", () => {

    fetch("/repo/"+repoName, {
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
            console.log("Original path: " + path);
            // we add the final "/" to the path
            var count = (path.match(/\//g) || []).length;
            console.log("Number of /: " + count);
            path = path + "/";
            if (path == "/repo/"+repoName+"/"){ // if we are in the root of the repository
                window.location.replace("/"); 
            }
            // There are two cases:
            // a) The redirection takes you to the root of the repository (path = "/repo/repoName/")
            // b) The redirection takes you to a folder (path = "/repo/repoName/folder")
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
    console.log(numberOfVisibleFilesAndFolders);
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
        console.log("We are sending the folder: " + folderName + " and the path: " + folderPath)    
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
    let myDropzone = new Dropzone(".dropzone", {
        url:'/upload-file',
        maxFilesize:104857600, // 100MB (GitHub limit)
        maxFiles:1,
        acceptedFiles: ".docx",
        addRemoveLinks:false,
        previewTemplate: '<div class="dz-preview dz-file-preview"></div>',
        sending: function(file, xhr, formData) {
            formData.append("repoName", repoName);
            formData.append("path", window.location.pathname);
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
}

// prevent small rectangles for dragging files
document.getElementById('add-file').addEventListener('submit', function(event) {
    event.preventDefault(); 
});