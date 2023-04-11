/**
 * Set the current bet settings.
 *
 * @param {string} betMode - Name of the betting mode
 * @param {number} allInUntil - Max value to go all in until. [0, ...]
 * @param {number} maxBetPercentage  - Max percentage amount to bet. [0, 100].
 * @param {number} maxBetAmount  - Max amount to ever bet. [0, ...]
 * @param {boolean} allInTournaments - Whether or not to go all in on tournaments.
 * @param {boolean} enableBetting  - Enable disable betting in the extension.
 * @param {boolean} dollarExhibitions - Enable disable betting $1 on exhibitions.
 * @returns
 */
function setBetSettings(
    betMode,
    allInUntil,
    maxBetPercentage,
    maxBetAmount,
    allInTournaments,
    enableBetting,
    dollarExhibitions
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
                    dollarExhibitions: dollarExhibitions,
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
 *      "dollarExhibitions": boolean,
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
 * @param {boolean} dollarExhibitions - Enable disable betting $1 on exhibitions.
 * @returns
 */
function initializeBetSettings(
    betMode,
    allInUntil,
    maxBetPercentage,
    maxBetAmount,
    allInTournaments,
    enableBetting,
    dollarExhibitions
) {
    return getBetSettings().then((betSettings) => {
        function getDefault(storedValue, defaultValue) {
            if (storedValue == null || storedValue == undefined) {
                return defaultValue
            }

            return storedValue
        }

        betMode = getDefault(betMode, betSettings.betMode)
        allInUntil = getDefault(allInUntil, betSettings.allInUntil)
        maxBetPercentage = getDefault(
            maxBetPercentage,
            betSettings.maxBetPercentage
        )
        maxBetAmount = getDefault(maxBetAmount, betSettings.maxBetAmount)
        allInTournaments = getDefault(
            allInTournaments,
            betSettings.allInTournaments
        )
        enableBetting = getDefault(enableBetting, betSettings.enableBetting)
        dollarExhibitions = getDefault(
            dollarExhibitions,
            betSettings.dollarExhibitions
        )

        return setBetSettings(
            betMode,
            allInUntil,
            maxBetPercentage,
            maxBetAmount,
            allInTournaments,
            enableBetting,
            dollarExhibitions
        )
    })
}

export { initializeBetSettings, setBetSettings, getBetSettings }
