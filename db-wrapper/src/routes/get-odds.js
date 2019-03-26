const express = require('express');
const router = express.Router();
const model = require('../models/model');

router.get('/', (req, res) => {
    if (!checkCorrectParams(req.query)) {
        return res.send("Incorrect Params!");
    }

    let fighter1 = {}, fighter2 = {};

    fighter1.name = req.query.fighter1;
    fighter2.name = req.query.fighter2;

    model.getFighterFightCount(fighter1.name)
    .then((result) => {
        fighter1.id = result.id;
        fighter1.matchCount = result.fightCount;
        return model.getFighterFightCount(fighter2.name);
    })
    .then((result) => {
        fighter2.id = result.id;
        fighter2.matchCount = result.fightCount;
        return model.getFighterWins(fighter1.name);
    })
    .then((result) => {
        fighter1.wins = result.winCount;
        return model.getFighterWins(fighter2.name);
    })
    .then((result) => {
        fighter2.wins = result.winCount;

        if (fighter1.matchCount != -1) {
            return model.getWinsAgainst(fighter1.id, fighter2.id);
        } else {
            return -1;
        }
    })
    .then((result) => {
        fighter1.winsAgainst = result;
        
        if (fighter2.matchCount != -1) {
            return model.getWinsAgainst(fighter2.id, fighter1.id);
        } else {
            return -1
        }
    })
    .then((result) => {
        fighter2.winsAgainst = result;

        res.json(calculateWinner(fighter1, fighter2));
    })
    .catch((error) => {
        console.log(error);
        res.send("something went wrong");
    });
});


// ------- Helper Functions -------

function checkCorrectParams(params) {
    if (("fighter1" in params) && ("fighter2" in params)) {
        return true;
    }
    return false;
}

function calculateWinner(fighter1, fighter2) {
    console.log(fighter1, fighter2);

    let fighter1prob, fighter2prob, winner;

    if ((fighter1.id == -1) && (fighter2.id != -1)) {
        fighter2prob = fighter2.wins / fighter2.matchCount;
        fighter1prob = 1 - (fighter2prob);
    } else if ((fighter1.id != -1) && (fighter2.id == -1)) {
        fighter1prob = fighter1.wins / fighter1.wins;
        fighter2prob = 1 - fighter1prob;
    } else if ((fighter1.id == -1) && (fighter2.id == -1)) {
        fighter1prob = 0.5;
        fighter2prob = 0.5;
    } else if (fighter1.winsAgainst != 0 || fighter2.winsAgainst != 0) {
        let totalFightsAgainst = fighter1.winsAgainst + fighter2.winsAgainst;
        fighter1prob = fighter1.winsAgainst / totalFightsAgainst;
        fighter2prob = 1 - fighter1prob;
    } else {
        fighter1prob = fighter1.wins / (fighter1.matchCount + fighter2.matchCount);
        fighter2prob = 1 - fighter1prob;
        console.log(fighter1prob, fighter2prob);
    }

    winner = (fighter1prob == fighter2prob ? "tie" : (fighter1prob > fighter2prob ? fighter1.name : fighter2.name));

    return {
        fighter1prob: fighter1prob.toFixed(2),
        fighter2prob: fighter2prob.toFixed(2),
        winner: winner
    };
}

module.exports = router;