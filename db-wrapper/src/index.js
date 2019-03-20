const express = require('express');
const bodyParser = require('body-parser');
const { Pool } = require('pg');
const fs = require('fs');

const app = express();
const port = 8080;
const creds = JSON.parse(fs.readFileSync(__dirname + '/creds.json'));

const pool = new Pool({
    user: creds.user,
    host: creds.host,
    database: creds.database,
    password: creds.password,
    port: 5432
});



app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.post('/add', (req, res) => {
    console.log(req.body);

    let player1 = req.body.player1;
    let player2 = req.body.player2;
    let tier = req.body.tier;
    let format = req.body.format;
    let winner = req.body.winner;

    let fighterID1, fighterID2, winnerID, dateID;

    addDate()
        .then((row) => {
            dateID = row.id;
            return selectFighterByName(player1.name)
        })
        .then((rows) => {
            if (rows.length == 0) {
                return addFighter(player1.name, tier);
            } else {
                return rows[0];
            }
        })
        .then((row) => {
            fighterID1 = row.id;
            return selectFighterByName(player2.name);
        })
        .then((rows) => {
            if (rows.length == 0) {
                return addFighter(player2.name, tier);
            } else {
                return rows[0];
            }
        })
        .then((row) => {
            fighterID2 = row.id;
            if (player1.name == winner) {
                winnerID = fighterID1;
            } else {
                winnerID = fighterID2;
            }
            return addMatch(fighterID1, fighterID2, player1.bet, player2.bet, winnerID, format, dateID)
        })
        .then((row) => {
            console.log(row);
        })
        .catch((err) => {
            console.log("Something went wrong", err);
        })

    res.send();
});

function addFighter(fighterName, tier) {
    const query = {
        text: "INSERT INTO fighters(name, tier, asof) VALUES($1, $2, CURRENT_DATE) RETURNING *",
        values: [fighterName, tier]
    }

    return new Promise((res, rej) => {
        pool.query(query)
            .then((queryResponse) => {
                res(queryResponse.rows[0])
            })
            .catch((err) => {
                rej(err);
            })
    })
}

function selectFighterByName(fighterName) {
    const query = {
        text: "SELECT * FROM fighters WHERE name = $1",
        values: [fighterName]
    }

    return new Promise((res, rej) => {
        pool.query(query)
            .then((queryResponse) => {
                res(queryResponse.rows);
            })
            .catch((err) => {
                rej(err);
            });
    });
}

function addMatch(fighterID1, fighterID2, bet1, bet2, winnerID, format, dateID) {
    const query = {
        text: "INSERT INTO matches(date, fighter_1, fighter_2, bet_1, bet_2, winner, format) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *",
        values: [dateID, fighterID1, fighterID2, bet1, bet2, winnerID, format]
    };

    return new Promise((res, rej) => {
        pool.query(query)
        .then((queryResponse) => {
            res(queryResponse.rows[0])
        })
        .catch((err) => {
            rej(err);
        });
    });
}

function addDate() {
    let dateItems = getCurrentDate();

    const query = {
        text: "INSERT INTO dates(time, date, day_of_week, month, year) VALUES(CURRENT_TIME, CURRENT_DATE, $1, $2, $3) RETURNING *",
        values: [dateItems["day_of_week"], dateItems["month"], dateItems["year"]]
    };

    return new Promise((res, rej) => {
        pool.query(query)
            .then((queryResponse) => {
                res(queryResponse.rows[0]);
            })
            .catch((err) => {
                rej(err);
            });
    });
}

function getCurrentDate() {
    const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
    const months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"];

    let d = new Date();

    return {
        "day_of_week": days[d.getDay()],
        "month": months[d.getMonth()],
        "year": d.getFullYear()
    };

}


app.listen(port, (err) => {
    if (err) {
        return console.log("Something went wrong.", err);
    }

    console.log("Now listening on:", port);
});

