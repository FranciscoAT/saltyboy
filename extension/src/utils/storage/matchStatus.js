/**
 * Store the current match status
 *
 * @param {string} currentStatus - Should be on of "ongoing" or "betting"
 * @param {boolean} betConfirmed
 * @param {boolean} loggedIn
 * @returns
 */
function setMatchStatus(currentStatus, betConfirmed, loggedIn) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                matchStatus: {
                    currentStatus: currentStatus,
                    betConfirmed: betConfirmed,
                    loggedIn: loggedIn,
                },
            },
            () => {
                res()
            }
        )
    })
}

/**
 * Get the current match status
 *
 * @returns {object} - Should be an object of the following form:
 *  ```
 *  {
 *      "currentStatus": "ongoing" | "betting",
 *      "betConfirmed": boolean,
 *      "loggedIn": boolean
 *  }
 */
function getMatchStatus() {
    return new Promise((res) => {
        chrome.storage.local.get(['matchStatus'], (result) => {
            res(result.matchStatus)
        })
    })
}

/**
 * Initializes the match status
 */
function initializeMatchStatus() {
    return setMatchStatus('betting', false, false)
}

export { setMatchStatus, getMatchStatus, initializeMatchStatus }
