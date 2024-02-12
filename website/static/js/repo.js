const backButton = document.querySelector("#backButton");
const searchInput = document.querySelector("[data-search");
const filesAndFolders = document.querySelectorAll(".content-box");
var repoName = document.title;
const folders = document.querySelectorAll("#folder");


// function to go back to home page
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
            window.location.replace("/");
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
        fetch("/repo/"+repoName, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ type: "open", folder: folderName }),
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
                window.location.replace("/repo/"+repoName+"/"+folderName);
            }
        })
        .catch(function (error) {
            console.error("Fetch error:", error);
        });
    });
});