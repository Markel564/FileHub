const backButton = document.querySelector("#backButton");


// go back to home page
backButton.addEventListener("click", () => {

    window.location.replace("/home");
})


// accept invitation
document.addEventListener("DOMContentLoaded", function() {

    var acceptInvitation = document.querySelectorAll(".btn-accept");

    acceptInvitation.forEach(function(button) {
        button.addEventListener("click", function() {
            
            const buttonId = button.id; // get the id of the button, which is the repoName
            
            // the owner will be in the same invitation header
            const invitationHeader = button.closest('.invitation-header');

            const inviterElement = invitationHeader.querySelector('#inviter');
            const owner = inviterElement.textContent;

            fetch("/invitations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ repoName: buttonId, owner: owner, type: "accept" }),
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
                    window.location.href = "/error";
                }
            }).catch(function (error) {
                console.error("Fetch error:", error);
            });
        }
    )}
)}
);


// decline invitation
document.addEventListener("DOMContentLoaded", function() {

    var declineInvitation = document.querySelectorAll(".btn-decline");

    declineInvitation.forEach(function(button) {
        button.addEventListener("click", function() {
            
            const buttonId = button.id; // get the id of the button, which is the repoName
            
            // the owner will be in the same invitation header
            const invitationHeader = button.closest('.invitation-header');

            const inviterElement = invitationHeader.querySelector('#inviter');
            const owner = inviterElement.textContent;

            fetch("/invitations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ repoName: buttonId, owner: owner, type: "decline" }),
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
            }).catch(function (error) {
                console.error("Fetch error:", error);
            });
        }
    )}
)}
);