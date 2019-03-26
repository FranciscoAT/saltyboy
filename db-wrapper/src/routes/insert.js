const express = require('express');
const router = express.Router();
const model = require('../models/model');

router.post('/', (req, res) => {
    let fighter1 = req.body.player1;
    let fighter2 = req.body.player2;
    let tier = req.body.tier;
    let format = req.body.format;
    let winner = req.body.winner;

    let dateID, winnerID;

    model.insertCurrentDate()
        .then((row) => {
            dateID = row.id;
            return model.insertFighter(fighter1.name, tier);
        })
        .then((row) => {
            fighter1.id = row.id;
            return model.insertFighter(fighter2.name, tier);
        })
        .then((row) => {
            fighter2.id = row.id;

            if (fighter1.name == winner) {
                winnerID = fighter1.id;
            } else {
                winnerID = fighter2.id;
            }
            return model.insertMatch(fighter1, fighter2, winnerID, format, dateID);
        })
        .then((row) => {
            console.log("Done Adding match.");
        })
        .catch((error) => {
            console.error("Something went wrong: ", error);
        });

    res.send();
});

module.exports = router;