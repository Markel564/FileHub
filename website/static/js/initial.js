submitButton = document.querySelector("#submitToken");

// send the token
submitButton.addEventListener("click", () => {

    const inptutToken = document.getElementById('token');

    const token = inptutToken.value;

    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({type: "token", token: token }),
    })
    .then(function (response) {
        if (response.ok) {
            return response.json(); 
        } else {
            throw new Error("Network response was not ok");
        }
    }).then(function (data) {
        if (data.status == "ok"){
            window.location.href = "/home";
        }else{
            window.location.reload();
        }
    })
}
);


