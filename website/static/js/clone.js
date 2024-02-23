// contains the functions for 'accepting the clonation' of the repository
// const repoName = document.querySelector("#headerName").textContent;

document.addEventListener("DOMContentLoaded", function () {

    // the structure is similar to delete-info.js, as both are windows used for confirmation

    // CLONATION CONFIRMATION
    function PostRequestClone() {
        console.log("Cloning the repository")
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
            console.log(data);
            if (data.status == "ok"){
                // window.location.replace("/");
                // window.location.reload();
                window.location.href = window.location.href;
            }
            if (data.status == "errorAlreadyCloned"){
                console.log("The repository is already cloned");
                // alert("The repository is already cloned");
                // window.location.reload();
                window.location.href = window.location.href;
                
            }
            
        })
        .catch(function (error) {
            console.error("Fetch error for clonation:", error);
        });
    }

    // CANCEL CLONATION
    function PostRequestCancel() {
            console.log("Canceling clonation")
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
                    // window.location.reload();
                    
                }
            })
            .catch(function (error) {
                console.error("Fetch error for clonation:", error);
            });
        }

    var acceptButton = document.getElementById("ok");
    var backButton = document.getElementById("back");

    acceptButton.addEventListener("click", PostRequestClone);
    backButton.addEventListener("click", PostRequestCancel);
});