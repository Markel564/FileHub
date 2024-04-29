// contains the functions for 'accepting the clonation' of the repository as well as the creation of new folder

document.addEventListener("DOMContentLoaded", function () {

    // the structure is similar to delete-info.js, as both are windows used for confirmation

    // CLONATION CONFIRMATION
    function PostRequestClone() {

        // obtain the path entered by the user in the input
        var path = document.getElementById("path").value;
        
        fetch("/repo/" + repoName + "/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({type: "clone-confirm", repoName: repoName, absolutePath: path}),
        })
        .then(function (response) {
            if (response.ok) {
                return response.json(); 
            } else {
                throw new Error("Network response was not ok");
            }
        })
        .then(function (data) {
            var errorContainer = document.getElementById("modal-content");
                
                var state = false;
                function toggleState() {
                    if (!state){ 
                        errorContainer.classList.remove("modal-content");
                        errorContainer.classList.add("hide")
                    }else{
                        errorContainer.classList.remove("hide");
                        errorContainer.classList.add("modal-content");
                    }
            }
            toggleState();

            if (data.status == "ok"  || data.status == "error"){
                window.location.href = window.location.href;
            }
            else{
                
                window.location.href = window.location.href;
                
            }
            
        })
        .catch(function (error) {
            console.error("Fetch error for clonation:", error);
        });
    }

    // CANCEL CLONATION
    function PostRequestCancel() {
            fetch("/repo/" + repoName + "/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({type: "clone-cancel"}),
            })
            .then(function (response) {
                if (response.ok) {
                    return response.json(); 
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function (data) {
                console.log(data);
                var errorContainer = document.getElementById("modal-content");
                    
                    var state = false;
                    function toggleState() {
                        if (!state){ 
                            errorContainer.classList.remove("modal-content");
                            errorContainer.classList.add("hide")
                        }else{
                            errorContainer.classList.remove("hide");
                            errorContainer.classList.add("modal-content");
                        }
                    }
                toggleState();
                if (data.status == "ok"){
                    
                }
                if (data.status == "errorAlreadyCloned"){
                    alert("The repository is already cloned");
                    
                }
            })
            .catch(function (error) {
                console.error("Fetch error for clonation:", error);
            });
        }

    var acceptButton = document.getElementById("ok-clone");
    var backButton = document.getElementById("back-clone");

    acceptButton.addEventListener("click", PostRequestClone);
    backButton.addEventListener("click", PostRequestCancel);
});




// CREATE FOLDER
document.addEventListener("DOMContentLoaded", function () {

    function PostRequestCreateFolder() {

        // obtain the name entered by the user in the input
        var folderName = document.getElementById("folder-name").value;

        // obtain the path of the folder within the repository
        let path = window.location.pathname;
        path = path.substring(6);
        path = path.substring(repoName.length);
        path = path.substring(1);
        if (path[path.length-1] != "/"){
            path = path + "/";
        }

        fetch("/repo/" + repoName + "/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({type: "create-folder", folderName: folderName, repoName: repoName, folderPath: path}),
        })
        .then(function (response) {
            if (response.ok) {
                return response.json(); 
            } else {
                throw new Error("Network response was not ok");
            }
        })
        .then(function () {
            
            folderWindow = document.getElementById("modal-folder");

            var state = false;
            function toggleState() {
                if (!state){ 
                    folderWindow.classList.remove("modal-folder");
                    folderWindow.classList.add("hide")
                }else{
                    folderWindow.classList.remove("hide");
                    folderWindow.classList.add("modal-folder");
                }
            }
            toggleState();

            window.location.href = window.location.href;

        })
        .catch(function (error) {
            console.error("Fetch error for creating a folder:", error);
        });
    }

    // CANCEL FOLDER CREATION

    function PostRequestCancelFolder() {

        fetch("/repo/" + repoName + "/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({type: "cancel-folder"}),
        })
        .then(function (response) {
            if (response.ok) {
                return response.json(); 
            } else {
                throw new Error("Network response was not ok");
            }
        })
        .then(function (data) {
            console.log(data);
            folderWindow = document.getElementById("modal-folder");

            var state = false;
            function toggleState() {
                if (!state){ 
                    folderWindow.classList.remove("modal-folder");
                    folderWindow.classList.add("hide")
                }else{
                    folderWindow.classList.remove("hide");
                    folderWindow.classList.add("modal-folder");
                }
            }
            toggleState();
        })
        .catch(function (error) {
            console.error("Fetch error for creating a folder:", error);
        });
    }

    var acceptButton = document.getElementById("ok-folder");
    var backButton = document.getElementById("back-folder");

    acceptButton.addEventListener("click", PostRequestCreateFolder);
    backButton.addEventListener("click", PostRequestCancelFolder);

});