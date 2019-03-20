const tmi = require('tmi.js');
const fs = require('fs');
var request = require('request');

const creds = JSON.parse(fs.readFileSync(__dirname + '/creds.json'));
const waifuID = '55853880';

const opts = {
    identity: {
        username: creds.username,
        password: creds.ouath
    },
    channels: [
        "saltybet"
    ]
};

const client = new tmi.client(opts);

client.on('message', onMessageHandler);
client.on('connected', onConnectHandler);

client.connect();

function onMessageHandler(target, context, msg, self) {
    if (self) {
        return;
    }

    if (context['user-id'] == waifuID) {
        console.log(`> ${msg}`);
        if (!inSync) {
            checkMessage(msg);
        }

        parseMessage(msg);
    }
}

function onConnectHandler(addr, port) {
    console.log(`Connected to ${addr}:${port}`);
}

// Logic to handle inputs
let inSync = false;
let currentTier, player1, player2, bet1, bet2, winner, format;

const openIdentifier = 'bets are open for ';
const lockedIdentifier = 'bets are locked.';
const winIdentifier = 'wins! payouts to team';

function parseMessage(msg) {
    if (!inSync) {
        return;
    }

    let msgLower = msg.toLowerCase();

    if (msgLower.includes(openIdentifier)) {
        if (msgLower.includes('matchmaking')) {
            format = 'matchmaking';
        } else if (msgLower.includes('tournament bracket')) {
            format = 'tournament';
        } else {
            format = 'exhibition';
        }
    }

    if (format == 'exhibition') {
        console.log("Ignoring exhibition matches");
        return;
    }

    if (msgLower.includes(openIdentifier)) {
        // Get the contestants
        const vsRegex = /.* vs .*!/g;
        let vsOutput = msgLower.replace(openIdentifier, '').match(vsRegex)[0].slice(0, -1).split(' vs ');
        player1 = vsOutput[0];
        player2 = vsOutput[1];

        // Get the tier
        const tierRegex = /[a-z] tier\)/g;
        let tierOutput = msgLower.match(tierRegex)[0].charAt(0).toUpperCase();
        currentTier = tierOutput;
    } else if (msgLower.includes(lockedIdentifier)) {
        const dollarRegex = /\$(,?\d+)*/g;
        let dollarOutput = msgLower.match(dollarRegex).map(dollarAmnt => parseInt(dollarAmnt.slice(1).replace(/,/g, '')));
        bet1 = dollarOutput[0];
        bet2 = dollarOutput[1];
    } else if (msgLower.includes(winIdentifier)) {
        const winnerRegex = /^.* wins!/g;
        let winnerOutput = msgLower.match(winnerRegex)[0].replace(' wins!', '');
        winner = winnerOutput;
        sendMatch();
    }
}


function checkMessage(msg) {
    let msgLower = msg.toLowerCase();
    if (msgLower.includes(openIdentifier)) {
        inSync = true;
    }
}

function sendMatch() {
    let data = {
        "player1": {
            "name": player1,
            "bet": bet1
        },
        "player2": {
            "name": player2,
            "bet": bet2
        },
        "tier": currentTier,
        "winner": winner,
        "format": format
    }

    request({
        url: "http://localhost:8080/add",
        method: "POST",
        json: true,
        body: data
    }, (err, res, body) => {
        console.log(res);
    });
}

