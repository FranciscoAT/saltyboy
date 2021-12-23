let fighterRedSpan = document.getElementById("fighter-red");
let fighterBlueSpan = document.getElementById("fighter-blue");
let formatSpan = document.getElementById("match-format");
let statusSpan = document.getElementById("match-status");
let lastUpdated = document.getElementById("last-updated");

// Initialize data on load
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
    fighterRedSpan.innerText = status["fighterRed"];
    fighterBlueSpan.innerText = status["fighterBlue"];
    formatSpan.innerText = status["format"];
    statusSpan.innerText = status["matchStatus"]
    lastUpdated.innerText = new Date().toString();
}
