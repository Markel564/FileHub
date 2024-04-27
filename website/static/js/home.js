const searchInput = document.querySelector("[data-search")
const repositoryElements = document.querySelectorAll(".repository");
const addRepoButton = document.querySelector("#addRepo");
const repositories = document.querySelectorAll('.repository-name');
const viewInvitations = document.querySelector("#viewInvitations");

// function to search for a repository
searchInput.addEventListener("input", (e) => {

    // Value of input
    const value = e.target.value.toLowerCase();
    
    repositoryElements.forEach((element) => {
        // Check if the repository name contains the value of the input
        const isVisible = element.querySelector("h1").textContent.toLowerCase().includes(value);

        // If the repository name does not contain the value of the input, hide it
        element.classList.toggle("hide", !isVisible);
    });

    // if the number of repositories is 0, display the div 'no-results'
    const numberOfVisibleRepositories = document.querySelectorAll(".repository:not(.hide)").length;
    
    const noResultsDiv = document.querySelector(".no-results");


    if (numberOfVisibleRepositories === 0) {
        noResultsDiv.style.display = "flex";

    } else {
        noResultsDiv.style.display = "none";
    }

});


// function to add a repository
addRepoButton.addEventListener("click", () => {
    // Create a POST request
    fetch("/home", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: "add" }),
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
            window.location.replace("/add");
        }
    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
});



// function to delete a repository (does not delete, rather shows up confirmation modal)
document.addEventListener("DOMContentLoaded", function () {
    

    // create a post request when the recycle bin is clicked
    var deleteButtons = document.querySelectorAll(".delete-repo");
    deleteButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            // Get the repository name from the data attribute
            var repoName = this.closest('.repository').getAttribute("data-repo-name");
            
            // Create a POST request
            fetch("/home", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ repo_name: repoName, type: "eliminate" }),
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
    
});




// function to move to the repository page
repositories.forEach(repository => {
    repository.addEventListener("click", () => {
        // obtain the repository name
        const repositoryName = repository.textContent.trim();
        fetch("/home", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({type: "repo", repo_name: repositoryName }),
        })
        .then(function (response) {
            if (response.ok) {
                return response.json(); 
            } else {
                throw new Error("Network response was not ok");
            }
        }).then(function (data) {
            repoName = data.repoName;
            if (data.status == "ok"){
                
                window.location.replace("/repo/"+repoName);
            }
            else{
                console.log("Error");
            }
        })
    });
});


// function to view invitations. It will take you to a new page with invitations

viewInvitations.addEventListener("click", () => {

    fetch("/home", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({type: "invitations"}),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    }).then(function (data) {
        if (data.status == "ok"){
            window.location.replace("/invitations");
        }
        else{
            console.log("Error");
        }
    })
});