/**
 * Model for the database. Contains useful functions for adding/retrieving from database as well as
 * pool for accessing database.
 * 
 * @author Francisco Trindade
 */


// ------ Constants ------
const { Pool } = require('pg');
const fs = require('fs');

const creds = JSON.parse(fs.readFileSync(__dirname + '/creds.json'));

const pool = new Pool({
    user: creds.user,
    host: creds.host,
    database: creds.database,
    password: creds.password,
    port: 5432
});

// ------ Common Functions ------

/**
 * Exectues given query and returns the newly added row if successful else rejects
 * 
 * @param {object} query Object for query for pool of form {text: SQL Query, values: [values, to, insert]}
 * @returns {Promise}
 */
function insertNewRow(query) {
    return new Promise((resolve, reject) => {
        pool.query(query)
            .then((response) => {
                resolve(response.rows[0]);
            })
            .catch((error) => {
                reject(error);
            });
    });
}

/**
 * Executes query and returns all rows if successful select else rejects
 * 
 * @param {object} query Object for query for pool of form {text: SQL Query, values: [values, to, insert]}
 * @returns {Promise}
 */
function selectQuery(query) {
    return new Promise((resolve, reject) => {
        pool.query(query)
            .then((response) => {
                resolve(response.rows);
            })
            .catch((error) => {
                reject(error);
            })
    });
}



// ------ Select Functions ------

/**
 * Returns all fighters with the given name
 * 
 * @param {string} fighterName The fighters name
 * @returns {Promise}
 */
function getFighterByName(fighterName) {
    const query = {
        text: "SELECT * FROM fighters WHERE name = $1",
        values: [fighterName]
    };

    return selectQuery(query);
}


// ------ Insertion Functions ------

/**
 * Inserts the given fighter. Will update fighter if rank has changed
 * @param {string} fighterName The fighters name
 * @param {string} tier The fighters current tier
 */
function insertFighter(fighterName, tier) {
    
}

