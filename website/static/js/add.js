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


// function to choose a directory and display the path in the input field
chooseButton.addEventListener('click', async function() {
    try {
        const directoryHandle = await window.showDirectoryPicker();
        const directoryPath = directoryHandle.name;
        // it is not possible to display the full path for security reasons, so a relative path is displayed
        localPathInput.value = '../' + directoryPath + "/"; //string that will be displayed in the input field
        
    } catch (error) {
        console.error(error);
    }
});


// function to create a new directory
createButton.addEventListener("click", () => {

    console.log("create button clicked");
    // get the values 
    const projectName = document.querySelector("#project-name").value;
    if (projectName == ""){
        alert("Project name not selected");
        return;
    }
    const projectDescription = document.querySelector("#description").value;
    // obtain readme (true or false)
    const readme = document.querySelector("#add-readme").checked;
    const privated = document.querySelector("#make-private").checked;

    const localPath = localPathInput.value;
    // eliminate the relative path
    localPath = localPath.replace("../", "");
    localPath = localPath.replace("/", "");
    if (localPath == ""){
        alert("Path not selected");
        return;
    }
    fetch("/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: "create", projectName: projectName, projectDescription: projectDescription, 
        path: localPath, readme: readme, private: privated}),
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
        if (data.status == "ok"){
            window.location.replace("/");
        }
        else if (data.status == "errorDuplicate"){
            alert("Project name already exists");
        }
    })
    .catch(function (error) {
        console.error("Fetch error:", error);
    });
})
