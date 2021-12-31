let loggedIn = document.getElementById("logged-in");
let statusSpan = document.getElementById("match-status");
let lastUpdated = document.getElementById("last-updated");
let betConfirmed = document.getElementById("bet-confirmed");

// Initialize data on load of popup
chrome.storage.local.get(["status"], (result) => {
    update(result.status);
});

chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace != "local") {
        return;
    }

    if ("status" in changes) {
        update(changes["status"]["newValue"]);
    }

});

function update(status) {
    loggedIn.innerText = status["loggedIn"];
    betConfirmed.innerText = status["betConfirmed"];
    statusSpan.innerText = status["matchStatus"]
    lastUpdated.innerText = new Date().toString();
}
