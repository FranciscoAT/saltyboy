/**
 * Model for the database. Contains useful functions for adding/retrieving from database as well as
 * pool for accessing database.
 * 
 * @author Francisco Trindade
 */


// ------ Constants ------
const { Pool } = require('pg');
const fs = require('fs');

const creds = JSON.parse(fs.readFileSync(__dirname + '/../creds.json'));

const pool = new Pool({
    user: creds.user,
    host: creds.host,
    database: creds.database,
    password: creds.password,
    port: 5432
});

// ------ Common Functions ------

/**
 * Exectues given query and returns the response inside of a promise
 * 
 * @param {object} query Object for query for the postgres pool
 * @returns {Promise}
 */
function executeQuery(query) {
    return new Promise((resolve, reject) => {
        pool.query(query)
            .then((response) => {
                resolve(response);
            })
            .catch((error) => {
                reject(error);
            });
    });
}

/**
 * Returns a custom object containing details about the current datetime
 * 
 * @returns {Object}
 */
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


// ------ Select Functions ------

/**
 * Returns all fighters with the given name
 * 
 * @param {string} fighterName The fighters name
 * @returns {Promise}
 */
function getFightersByName(fighterName) {
    const query = {
        text: "SELECT * FROM fighters WHERE name = $1",
        values: [fighterName]
    };

    return new Promise((resolve, reject) => {
        executeQuery(query)
            .then((result) => {
                if (result.rows !== 'undefined') {
                    resolve(result.rows);
                } else {
                    resolve([]);
                }
            })
            .catch((error) => {
                reject(error);
            });
    });
}


// ------ Insertion Functions ------

/**
 * Inserts the given fighter. Will update fighter if rank has changed
 * @param {string} fighterName The fighters name
 * @param {string} tier The fighters current tier
 * @returns {Promise}
 */
function insertFighter(fighterName, tier) {
    return new Promise((resolve, reject) => {
        getFightersByName(fighterName)
            .then((rows) => {
                if (rows.length == 0) {
                    const query = {
                        text: "INSERT INTO fighters(name, tier, asof) VALUES ($1, $2, CURRENT_DATE) RETURNING *",
                        values: [fighterName, tier]
                    };
                    return executeQuery(query);
                } else {
                    return rows;
                }
            })
            .then((response) => {
                if (Array.isArray(response)) {
                    resolve(response[0])
                } else {
                    console.log("Inserted new fighter with id: ", response.rows[0].id);
                    resolve(response.rows[0]);
                }
            })
            .catch((error) => {
                reject(error);
            });
    });
}


/**
 * Inserts the current date time into the date table and returns promise giving the new date row
 * 
 * @returns {Promise}
 */
function insertCurrentDate() {
    const dateItems = getCurrentDate();

    const query = {
        text: "INSERT INTO dates(time, date, day_of_week, month, year) VALUES(CURRENT_TIME, CURRENT_DATE, $1, $2, $3) RETURNING *",
        values: [dateItems["day_of_week"], dateItems["month"], dateItems["year"]]
    };

    return new Promise((resolve, reject) => {
        executeQuery(query)
            .then((response) => {
                console.log("Inserted new date with id: ", response.rows[0].id);
                resolve(response.rows[0]);
            })
            .catch((error) => {
                reject(error);
            });
    });
}

/**
 * Inserts the a new match. Then returns a promise resolving with the new inserted row
 * 
 * @param {Object} fighter1 Fighter 1 contains at least id and bet
 * @param {Object} fighter2 Fighter 2 contains at least id and bet
 * @param {Integer} winnerID The fighter id winner
 * @param {String} format The format of the match (tournament | matchmaking)
 * @param {Integer} dateID The date id of the fight
 * @returns {Promise}
 */
function insertMatch(fighter1, fighter2, winnerID, format, dateID) {
    const query = {
        text: "INSERT INTO matches(date, fighter_1, fighter_2, bet_1, bet_2, winner, format) VALUES($1, $2, $3, $4, $5, $6, $7) RETURNING *",
        values: [dateID, fighter1.id, fighter2.id, fighter1.bet, fighter2.bet, winnerID, format]
    };

    return new Promise((resolve, reject) => {
        executeQuery(query)
        .then((response) => {
            console.log("Inserted new match with id: ", response.rows[0].id);
            resolve(response.rows[0]);
        })
        .catch((error) => {
            reject(error);
        });
    });
}


// ------ Module Export ------

module.exports = {
    insertCurrentDate: insertCurrentDate,
    insertFighter: insertFighter,
    insertMatch: insertMatch
};