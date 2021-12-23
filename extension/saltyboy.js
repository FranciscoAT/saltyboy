const RUN_INTERVAL = 5000;
const SALTY_BOY_URL = "https://www.salty-boy.com";
let LAST_STATUS = null;
let FETCHED_FIGHTER_DATA = false;
let CURR_OUT_OF_DATE_ERR_COUNT = 0;


function run() {
    let status = updateStatus();
    if (status["loggedIn"] == false || checkStatusHealth(status) == false) {
        return;
    }
    getFighterData(status);
}

function updateStatus() {
    let loggedIn = document.getElementsByClassName("nav-text").length == 0;
    let odds = document.getElementById("odds");
    let fighterRed = "unknown";
    let fighterBlue = "unknown";
    let matchStatus = "unknown";
    let format = "unknown";
    let betConfirmed = false;

    if (loggedIn) {
        if (odds.getInnerHTML() == "" || document.getElementById("betconfirm") != null)  {
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
    }

    let status = {
        "fighterRed": fighterRed,
        "fighterBlue": fighterBlue,
        "matchStatus": matchStatus,
        "format": format,
        "betConfirmed": betConfirmed,
        "loggedIn": loggedIn
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

    fetch(`${SALTY_BOY_URL}/current_match`, { method: "get"})
        .then(res => res.json())
        .then(data => {
            placeBets(data);
        })
        .catch(err => {
            console.error("Something went wrong getting current match from server.", err);
            FETCHED_FIGHTER_DATA = false;
        });
}

function placeBets(matchData) {
    let wager = document.getElementById("wager");
    let fighterRed = document.getElementById("player1");
    let fighterBlue = document.getElementById("player2");

    // Last sanity check
    if (fighterRed.value != matchData["fighter_red"] || fighterBlue.value != matchData["fighter_blue"]) {
        CURR_OUT_OF_DATE_ERR_COUNT += 1;
        if (CURR_OUT_OF_DATE_ERR_COUNT > 5) {
            console.warn("Current Match from server is out of date", fighterRed.value, fighterBlue.value, matchData);
        }
        return;
    }

    CURR_OUT_OF_DATE_ERR_COUNT = 0;

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

setInterval(run, 5000);
