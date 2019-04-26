/*global $:true*/
/*eslint-env browser*/

$(document).ready(() => {
    let $player1 = $("#player1");
    let $player2 = $("#player2");
    let currentStatus = null;
    let betsPlaced = false;

    /**
     * Gets the curent fighters names when bets are open else false
     * @returns {false || array} retval Returns array of fighter names or false
     */
    function getFighters() {
        let retval = false;
        if (
            $player1.attr("disabled") != "disabled" &&
            currentStatus != "betsopen" &&
            $player2.attr("disabled") != "disabled"
        ) {
            currentStatus = "betsopen";
            let fighter1Name = $player1.val().toLowerCase();
            let fighter2Name = $player2.val().toLowerCase();
            retval = [fighter1Name, fighter2Name];
        }

        return retval;
    }

    function sendFighters(currentFighters) {
        console.log("sending fighter request with fighters", currentFighters);
        const msgContent = {
            action: "newfight",
            value: currentFighters,
        };

        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(msgContent, response => {
                if (response == false) {
                    reject("Something went wrong with message.");
                } else {
                    resolve(response);
                }
            });
        });
    }

    function checkLogin() {
        let $loginButton = $("li.nav-text a");

        if ($loginButton.attr("href") === "./authenticate?signin=1") {
            return false;
        }

        return true;
    }

    function bet(fighterResponse) {
        if (
            currentStatus == "betsclosed" ||
            (currentStatus == "betsopen" && betsPlaced == true)
        ) {
            return;
        }

        console.log("betting");

        let $wager = $("#wager");
        $wager.val("1");

        betsPlaced = true;
        currentStatus = "betsclosed";
        if (fighterResponse.fighter1prob > fighterResponse.fighter2prob) {
            $player1.click();
        } else {
            $player2.click();
        }
    }

    setInterval(() => {
        console.log(currentStatus);
        if (!checkLogin()) {
            return;
        }

        let currentFighters = getFighters();

        if (currentFighters != false) {
            sendFighters(currentFighters)
                .then(response => {
                    console.log(JSON.parse(response));
                    bet(JSON.parse(response));
                })
                .catch(error => {
                    console.log(error);
                });
        }
    }, 1000);
});
