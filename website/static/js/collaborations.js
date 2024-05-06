const backButton = document.querySelector("#backButton");


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



