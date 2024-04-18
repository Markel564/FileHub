const backButton = document.querySelector("#backButton");


// go back to the previous folder
backButton.addEventListener("click", () => {

    fetch("/add", {  // we can reuse the function we used to add a repository to go back to the home page
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
            window.location.href = "/";
        }
    }).catch(function (error) {
        console.error("Fetch error:", error);
    });
})