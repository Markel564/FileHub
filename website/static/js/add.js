const backButton = document.querySelector("#backButton");
const chooseButton = document.querySelector("#chooseButton");
const createButton = document.querySelector("#createButton");
var localPathInput = document.querySelector("#local-path");



// function to go back to home page
backButton.addEventListener("click", () => {
    fetch("/add", {
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
            window.location.replace("/home");
        }
    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });

})



// function to create a new repository
createButton.addEventListener("click", (event) => {
    
    event.preventDefault();
    // get the values
    const projectName = document.querySelector("#project-name").value;
    if (projectName == ""){
        alert("Project name not selected");
        return;
    }
    const projectDescription = document.querySelector("#description").value;
    const privated = document.querySelector("#make-private").checked;

    const path_of_repo = document.getElementById('path-of-repo');
    const repoPath = path_of_repo.value;
    
    // console.log(path_of_repo, repoPath);
    fetch("/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({  type: "create", 
                                projectName: projectName, 
                                projectDescription: projectDescription, 
                                private: privated,
                                repoPath: repoPath 
                            }),
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
            window.location.replace("/home");
        }
        else{
            window.location.href = "/error"
        }
    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
})
