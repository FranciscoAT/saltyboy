const RUN_INTERVAL = 5000;
const SALTY_BOY_URL = "https://www.salty-boy.com";
let LAST_STATUS = null;
let FETCHED_FIGHTER_DATA = false;


function run() {
    let status = updateStatus();
    if (checkStatusHealth(status) == false) {
        return;
    }
    getFighterData(status);
}

function updateStatus() {
    let odds = document.getElementById("odds");
    let fighterRed = "unknown";
    let fighterBlue = "unknown";
    let matchStatus = "unknown";
    let format = "unknown";
    let betConfirmed = false;
    if (odds.getInnerHTML() == "")  {
        fighterRed = document.getElementById("player1").value;
        fighterBlue = document.getElementById("player2").value;
        matchStatus = "betting";
        betConfirmed = document.getElementById("betconfirm") != null;
    } else {
        fighterRed = odds.getElementsByClassName("redtext")[0].innerText.trim();
        fighterBlue = odds.getElementsByClassName("bluetext")[0].innerText.trim();
        matchStatus = "ongoing";
    }

    let footerAlertText = document.getElementById("footer-alert").innerText;
    if (footerAlertText.includes("more matches until the next tournament!")) {
        format = "matchmaking";
    } 

    let status = {
        "fighterRed": fighterRed,
        "fighterBlue": fighterBlue,
        "matchStatus": matchStatus,
        "format": format,
        "betConfirmed": betConfirmed,
    };

    chrome.storage.local.set({"status": status}, () => {});

    if (LAST_STATUS != status) {
        LAST_STATUS = status;
        FETCHED_FIGHTER_DATA = false;
    }

    return status;
}

function getFighterData(status) {
    if (status["matchStatus"] != "betting" || status["betConfirmed"] == true) {
        return;
    }

    FETCHED_FIGHTER_DATA = true;

    fetch(generateRequest(status["fighterRed"]), { method: "get"})
    .then(res => res.json())
    .then(fighterRedData => {
        chrome.storage.local.set({"fighterRedData": fighterRedData}, () => {
            return fetch(generateRequest(status["fighterBlue"]), {method: "get"})
        });
    })
    .then(res => res.json())
    .then(fighterBlueData => {
        chrome.storage.local.get("fighterRedData", (fighterRedData) => {
            placeBets(fighterRedData, fighterBlueData);
        })
    })
    .catch(err => {
        console.error("Something went wrong.", err);
        FETCHED_FIGHTER_DATA = false;
    })
}

function placeBets(fighterRedData, fighterBlueData) {
    let wager = document.getElementById("wager");
    let fighterRed = document.getElementById("player1");
    let fighterBlue = document.getElementById("player2");

    // Last sanity check
    if (fighterRed.value != fighterRedData["name"] || fighterBlue.value != fighterBlueData["name"]) {
        console.error("Returned fighter data did not match current bets.", fighterRedData, fighterBlueData);
        return;
    }

    // TODO: better implementation of logic
    wager.value = "1";
    fighterRed.click();
}

function checkStatusHealth(status) {
    for (const key in status) {
        if (status[key] == "unknown") {
            return false;
        }
    }
    return true;
}

function generateRequest(fighterName) {
    return `${SALTY_BOY_URL}/fighters?${encodeURIComponent(fighterName)}`
}




setInterval(run, 5000);
