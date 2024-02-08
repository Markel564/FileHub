const backButton = document.querySelector("#backButton");
var repoName = document.title;

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
