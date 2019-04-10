$(document).ready(() => {
    let $player1 = $('#player1');
    let $player2 = $('#player2');
    let currentStatus = null;


    function getFighters() {
        let retval = false;
        if (($player1.attr('disabled') != 'disabled') && (currentStatus != 'betsopen')) {
            currentStatus = 'betsopen';
            let fighter1Name = $player1.val();
            let fighter2Name = $player2.val();
            retval = [fighter1Name, fighter2Name];
        } else if (($player1.attr('disabled') == 'disabled') && currentStatus != 'betsclosed') {
            currentStatus = 'betsclosed';
        }
        return retval;
    }

    function sendFighters(currentFighters) {
        console.log("sending fighter request with fighters", currentFighters);
        const msgContent = {
            action: 'newfight',
            value: currentFighters
        };

        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(msgContent, (response) => {
                if (response == false) {
                    reject("Something went wrong with message.");
                } else {
                    resolve(response);
                }
            });
        });
    }


    setInterval(() => {
        let currentFighters = getFighters();

        if (currentFighters != false) {
            sendFighters(currentFighters)
                .then((response) => {
                    console.log(JSON.parse(response));
                })
                .catch((error) => {
                    console.log(error);
                });
        }

    }, 500);
});