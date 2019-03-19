$(document).ready(() => {
    let $player1 = $('#player1');
    let $player2 = $('#player2');
    let $betStatus = $('#betstatus');
    let $matchStyle = $('#footer-alert');
    let $betAmounts = $('#odds');
    let $odds = $('#lastbet');

    let betStatus;
    let tierSet = false;
    let currentTier = null;


    function init() {
        updateStatus();
    }


    function getBetStatus() {
        let statusText = ($betStatus.html()).toLowerCase();
        if (statusText.includes('open')) {
            return 'open';
        } else if (statusText.includes('wins')) {
            return 'win';
        }
        return 'closed';
    }

    function updateStatus() {
        let newStatus = getBetStatus();

        if (newStatus != betStatus) {
            betStatus = newStatus;
            return true;
        }

        return false;
    }

    function sendMatchResults() {
        let betAmounts = ($betAmounts.text()).match(/\$\d*(,\d*)*/g);
        let odds = ($odds.text()).replace(' ', '').split(':');
        let winnerName = $betStatus.split(' wins!')[0];

        let data = {
            "player1": {
                "name": $player1.val(),
                "amount": betAmounts[0],
                "odds": odds[0]
            },
            "player2": {
                "name": $player2.val(),
                "amount": betAmounts[1],
                "odds": odds[1]
            },
            "winner": winnerName
        };

        console.log(data);
    }


    function setCurrentTier() {
        // let $waifuMessages = $('div[data-user="waifu4u"] .message span[data-a-target="chat-message-text"]');
        let $waifuBody = $('#chat-frame-stream').contents().find('body');
        let $waifuRoot = $waifuBody.find('#root');

        console.log($waifuBody);
    }

    init();

    // setInterval(() => {
    //     let updated = updateStatus();

    //     if (updated && betStatus == 'win') {
    //         sendMatchResults();
    //     }
    // }, 500);
});