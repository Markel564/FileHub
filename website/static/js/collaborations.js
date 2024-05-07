const backButton = document.querySelector("#backButton");
const addCollaborator = document.querySelector("#addCollaborator");
const cancelCollaborator = document.querySelector("#cancel-collab");
const sendCollaborator = document.querySelector("#ok-collab");


// go back to repository page

backButton.addEventListener("click", () => {

    let path = window.location.pathname;
    
    // we have to eliminate the last part of the path
    let newPath = path.split("/").slice(0, -1).join("/");
    newPath = newPath + "/";

    window.location.replace(newPath);

});


// funcion to remove a collaborator from the repository
document.addEventListener("DOMContentLoaded", () => {


    var removeCollaboratorButtons = document.querySelectorAll(".remove-collaborator");

    removeCollaboratorButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            // Get the collaborator name from the data attribute
            
            const collaboratorName = button.closest('.collaboration')?.querySelector('.column h1')?.textContent;
            const repoName = document.querySelector('#headerName').textContent;
            
            // Create a POST request
            fetch("/repo/" + repoName + "/collaborators", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ repoName: repoName, collaboratorName: collaboratorName, type: "remove" }),
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
})



// function to add a collaborator to the repository (open modal)
addCollaborator.addEventListener("click", () => {

    var AddContainertainer = document.getElementById("modal-collaborator");
    var state = false; 
    function toggleState() {
                            
            if (state){ // if state is true, then hide the modal
                AddContainertainer.classList.remove("modal-content");
                AddContainertainer.classList.add("hide")
            }else{
                AddContainertainer.classList.remove("hide");
                AddContainertainer.classList.add("modal-content");
            }
    }               
    toggleState();
});

// function to cancel collaborator addition (close modal)
cancelCollaborator.addEventListener("click", () => {

    var AddContainertainer = document.getElementById("modal-collaborator");
    var state = true;
    function toggleState() {
                            
            if (state){ // if state is true, then hide the modal
                AddContainertainer.classList.remove("modal-content");
                AddContainertainer.classList.add("hide")
            }else{
                AddContainertainer.classList.remove("hide");
                AddContainertainer.classList.add("modal-content");
            }
    }
    toggleState();
});


// function to send the request to add a collaborator to the repository
sendCollaborator.addEventListener("click", () => {

    // get the values
    const searchInput = document.querySelector('#searchBar input[data-search]');

    const collaboratorName = searchInput.value;

    const checkboxAdmin = document.querySelector('#rowCollab #AdminCheck');
    const checkboxWriter = document.querySelector('#rowCollab #WriterCheck');
    const checkboxReader = document.querySelector('#rowCollab #ReaderCheck');

    const isCheckedAdmin = checkboxAdmin.checked;
    const isCheckedWriter = checkboxWriter.checked;
    const isCheckedReader = checkboxReader.checked;

    const repoName = document.querySelector('#headerName').textContent;

    fetch("/repo/" + repoName + "/collaborators", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({  repoName: repoName, 
                                collaboratorName: collaboratorName, 
                                type: "add", 
                                admin: isCheckedAdmin, 
                                writer: isCheckedWriter, 
                                reader: isCheckedReader }),
    }).then(function (response) {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error("Network response was not ok");
        }
    }).then(function (data) {
        if (data.status == "ok"){
            window.location.reload();
        }else{
            window.location.reload();
        }
    }).catch(function (error) {
        console.error("Fetch error:", error);
    });

});

