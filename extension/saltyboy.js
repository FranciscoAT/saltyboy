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
        } else if (footerAlertText == "Tournament mode start!" || footerAlertText.includes("characters are left in the bracket!")) {
            format = "tournament";
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
    let wagerInput = document.getElementById("wager");
    let fighterRedBtn = document.getElementById("player1");
    let fighterBlueBtn = document.getElementById("player2");

    // Last sanity check
    if (fighterRedBtn.value != matchData["fighter_red"] || fighterBlueBtn.value != matchData["fighter_blue"]) {
        CURR_OUT_OF_DATE_ERR_COUNT += 1;
        if (CURR_OUT_OF_DATE_ERR_COUNT > 5) {
            console.warn("Current Match from server is out of date", fighterRedBtn.value, fighterBlueBtn.value, matchData);
        }
        return;
    }

    let balance = parseInt(document.getElementById("balance").innerText().replace(",", ""));
    CURR_OUT_OF_DATE_ERR_COUNT = 0;

    let wagerAmount = null;
    let betColour = null;

    if (matchData["match_format"] == "exhibition") {
        // We don't want to bet on exhibition matches
        wagerAmount = 1;
        betColour = "red";
    } else if (matchData["fighter_red_info"] == null || matchData["fighter_blue_info"] == null) {
        // We cannot accurately bet on matches we have no stats for
        wagerAmount = 1;
        betColour = "red";
    } else {
        // TODO: more logic needs to go here
    }

    if (matchData["match_format"] == "tournament") {
        // Always bet max on tournament
        wagerAmount = balance;
    }

    // TODO: better implementation of logic
    wagerInput.value = wagerAmount.toString();
    if (betColour == "red") {
        fighterRedBtn.click();
    } else {
        fighterBlueBtn.click();
    }
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
