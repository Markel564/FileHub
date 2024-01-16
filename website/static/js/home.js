const searchInput = document.querySelector("[data-search")
const repositoryElements = document.querySelectorAll(".repository");


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





