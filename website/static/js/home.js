const searchInput = document.querySelector("[data-search")
const repositoryElements = document.querySelectorAll(".repository");

// function to search for a repository
searchInput.addEventListener("input", (e) => {
    // Obtain the names of the repositories
    repositoryElements.forEach((element) => {
        const repositoryName = element.querySelector("h1").textContent;
        console.log(repositoryName); 
    });

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
        console.log("No results");
        noResultsDiv.style.display = "flex";

    } else {
        noResultsDiv.style.display = "none";
    }

});



// function to delete a repository
document.addEventListener("DOMContentLoaded", function () {
    // Select the elements with the "delete-repo" class
    var deleteButtons = document.querySelectorAll(".delete-repo");
    deleteButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            // Get the repository name from the data attribute
            var repoName = this.closest('.repository').getAttribute("data-repo-name");

            // Create a POST request
            fetch("/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ repo_name: repoName, type: "eliminate" }),
            })
            .then(function (response) {
                if (response.ok) {
                    return response.text(); 
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function (data) {
                var errorContainer = document.getElementById("info-container");
                errorContainer.classList.toggle("show-info");
                errorContainer.innerHTML = data;
            })
            .catch(function (error) {
                console.error("Fetch error:", error);
            });
        });
    });
});


