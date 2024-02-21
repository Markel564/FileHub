document.addEventListener("DOMContentLoaded", function () {

    // ELIMINATION CONFIRMATION
    function PostRequestEliminate() {

        fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({type: "eliminate-confirm" }),
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
            var errorContainer = document.getElementById("info-container");
            
            var state = false;
            function toggleState() {
                if (!state){ 
                    errorContainer.classList.remove("show-info");
                    errorContainer.classList.add("hide")
                }else{
                    errorContainer.classList.remove("hide");
                    errorContainer.classList.add("show-info");
                }
            }
            toggleState();
            window.location.replace("/");
        }
    })
    .catch(function (error) {
        console.error("Fetch error for elimination:", error);
    });
    }

    // CANCEL ELIMINATION
    function PostRequestCancel() {

    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({type: "eliminate-cancel" }),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    })
    .then(function (data) {
        var errorContainer = document.getElementById("modal-content");
            
            var state = false;
            function toggleState() {
                if (!state){ 
                    errorContainer.classList.remove("modal-content");
                    errorContainer.classList.add("hide")
                }else{
                    errorContainer.classList.remove("hide");
                    errorContainer.classList.add("modal-content");
                }
            }
            toggleState();
    })
    .catch(function (error) {
        console.error("Fetch error", error);
    });
    }


    var removeButton = document.querySelector("#remove");
    var backButton = document.querySelector("#back");

    removeButton.addEventListener("click", function () {
        PostRequestEliminate();
    });

    backButton.addEventListener("click", function () {
        PostRequestCancel();
    });

});