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
            console.log(path);
            if (path == "/repo"){
                window.location.replace("/");
            }
            else
            window.location.replace(path);

        }
    })
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