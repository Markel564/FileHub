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
            window.location.replace("/");
        }
    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });

})



// function to create a new directory
createButton.addEventListener("click", (event) => {
    
    event.preventDefault();
    // get the values
    const projectName = document.querySelector("#project-name").value;
    if (projectName == ""){
        alert("Project name not selected");
        return;
    }
    const projectDescription = document.querySelector("#description").value;
    const readme = document.querySelector("#add-readme").checked;
    const privated = document.querySelector("#make-private").checked;
    
    fetch("/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({  type: "create", 
                                projectName: projectName, 
                                projectDescription: projectDescription, 
                                readme: readme, 
                                private: privated 
                            }),
    })
    .then(function (response) {
        console.log(response.status);
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    })
    .then(function (data) {
        console.log(data);
        if (data.status == "ok"){
            window.location.replace("/");
        }
        else if (data.status == "errorDuplicate"){
            alert("Project name already exists");
        }
        else if (data.status == "errorCreation"){
            window.location.replace("/error");
        }
    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
})
