/**
 * Set the current bet settings.
 *
 * @param {string} betMode - Name of the betting mode
 * @param {number} allInUntil - Max value to go all in until. [0, ...]
 * @param {number} maxBetPercentage  - Max percentage amount to bet. [0, 100].
 * @param {number} maxBetAmount  - Max amount to ever bet. [0, ...]
 * @param {boolean} allInTournaments - Whether or not to go all in on tournaments.
 * @param {boolean} enableBetting  - Enable disable betting in the extension.
 * @param {boolean} exhibitionBet - Amount to bet on exhibitions.
 * @param {boolean} upsetMode - Bet with upset mode.
 * @param {object} betTier - An object of the form {<tier>: <boolean>} for all tiers A, B, P, S, X
 * @returns
 */
function setBetSettings(
    betMode,
    allInUntil,
    maxBetPercentage,
    maxBetAmount,
    allInTournaments,
    enableBetting,
    exhibitionBet,
    upsetMode,
    betTier
) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                betSettings: {
                    betMode: betMode,
                    allInUntil: allInUntil,
                    maxBetPercentage: maxBetPercentage,
                    maxBetAmount: maxBetAmount,
                    allInTournaments: allInTournaments,
                    enableBetting: enableBetting,
                    exhibitionBet: exhibitionBet,
                    upsetMode: upsetMode,
                    betTier: betTier,
                },
            },
            () => {
                res()
            }
        )
    })
}

/**
 *
 * @returns {object} - Returns an object of the form:
 *  ```
 *  {
 *      "betMode": string,
 *      "allInUntil": number [0, ...],
 *      "maxBetPercentage": number [0, 100],
 *      "allInTournaments": boolean,
 *      "enableBetting": boolean,
 *      "exhibitionBet": boolean,
 *      "upsetMode": boolean,
 *      "betTier": {x: true, ...}
 *  }
 *  ```
 */
function getBetSettings() {
    return new Promise((res) => {
        chrome.storage.local.get(['betSettings'], (result) => {
            res(result.betSettings)
        })
    })
}

/**
 * Initializes storage of betSettings if not already set
 *
 * @param {string} betMode - Name of the betting mode
 * @param {number} allInUntil - Max value to go all in until. [0, ...]
 * @param {number} maxBetPercentage  - Max percentage amount to bet. [0, 100].
 * @param {number} maxBetAmount  - Max amount to ever bet. [0, ...]
 * @param {boolean} allInTournaments - Whether or not to go all in on tournaments.
 * @param {boolean} enableBetting  - Enable disable betting in the extension.
 * @param {boolean} exhibitionBet - Amount to bet on exhibitions.
 * @param {boolean} upsetMode - Bet with upset mode.
 * @param {object} betTier - An object of the form {<tier>: <boolean>} for all tiers A, B, P, S, X
 * @returns
 */
function initializeBetSettings(
    betMode,
    allInUntil,
    maxBetPercentage,
    maxBetAmount,
    allInTournaments,
    enableBetting,
    exhibitionBet,
    upsetMode,
    betTier
) {
    return getBetSettings().then((betSettings) => {
        if (betSettings != null || betSettings != null) {
            function getDefault(defaultValue, key) {
                if (!betSettings.hasOwnProperty(key)) {
                    return defaultValue
                }

                let storedValue = betSettings[key]

                if (storedValue == null || storedValue == undefined) {
                    return defaultValue
                }

                return storedValue
            }

            betMode = getDefault(betMode, 'betMode')
            allInUntil = getDefault(allInUntil, 'allInUntil')
            maxBetPercentage = getDefault(maxBetPercentage, 'maxBetPercentage')
            maxBetAmount = getDefault(maxBetAmount, 'maxBetAmount')
            allInTournaments = getDefault(allInTournaments, 'allInTournaments')
            enableBetting = getDefault(enableBetting, 'enableBetting')
            exhibitionBet = getDefault(exhibitionBet, 'exhibitionBet')
            upsetMode = getDefault(upsetMode, 'upsetMode')
            betTier = getDefault(betTier, 'betTier')
        }

        return setBetSettings(
            betMode,
            allInUntil,
            maxBetPercentage,
            maxBetAmount,
            allInTournaments,
            enableBetting,
            exhibitionBet,
            upsetMode,
            betTier
        )
    })
}

export { initializeBetSettings, setBetSettings, getBetSettings }
