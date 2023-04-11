import * as matchDataStorage from '../utils/storage/matchData.js'
import * as betSettingsStorage from '../utils/storage/betSettings.js'
import * as winningsStorage from '../utils/storage/winnings.js'
import * as matchStatusStorage from '../utils/storage/matchStatus.js'
import * as debugStorage from '../utils/storage/debugSettings.js'

// // Betting Imports
import naiveBet from './bet_modes/naive.js'
import passiveBet from './bet_modes/passive.js'
import rngBet from './bet_modes/rng.js'
import eloTierBet from './bet_modes/eloTier.js'
import eloBet from './bet_modes/elo.js'
import upsetBet from './bet_modes/upset.js'

const RUN_INTERVAL = 5000
const SALTY_BOY_URL = 'https://www.salty-boy.com'
const BET_MODES = {
    naive: naiveBet,
    passive: passiveBet,
    rng: rngBet,
    elo: eloBet,
    eloTier: eloTierBet,
    upset: upsetBet,
}

// Bet Settings, values listed are defaults on init
let ALL_IN_UNTIL = 0
let MAX_BET_PERCENTAGE = 5
let MAX_BET_AMOUNT = 0
let BET_MODE = 'naive'
let ALL_IN_TOURNAMENTS = true
let ENABLE_BETTING = true
let DOLLAR_EXHIBITIONS = true

// Extension State Values
let LAST_STATUS = null
let FETCH_FIGHTER_DATA = true
let CURR_OUT_OF_DATE_ERR_COUNT = 0

// Balance Tracking
let PREV_BALANCE = null

// Debug Information
let DEBUG_ENABLED = false

/**
 * Main logic loop of the application.
 *
 * @returns
 */
function run() {
    let saltyBetStatus = getSaltyBetStatus()

    if (LAST_STATUS != saltyBetStatus) {
        // We only want to re-fetch fighter data in the event we go from
        // ongoing into betting.
        if (
            LAST_STATUS != null &&
            LAST_STATUS.currentStatus == 'ongoing' &&
            saltyBetStatus.currentStatus == 'betting'
        ) {
            FETCH_FIGHTER_DATA = true
        }

        LAST_STATUS = saltyBetStatus
    }

    if (FETCH_FIGHTER_DATA == false) {
        return
    }

    getSaltyBoyMatchData().then((matchData) => {
        placeBets(matchData, saltyBetStatus)
    })
}

/**
 * Get the status of Salty Bet by reading elements from the DOM.
 *
 * @returns
 */
function getSaltyBetStatus() {
    let betStatus = document.getElementById('betstatus')

    let currentStatus = 'unknown'
    let loggedIn = document.getElementById('rank') != null
    let betConfirmed = false

    if (loggedIn) {
        if (betStatus.innerText == 'Bets are OPEN!') {
            currentStatus = 'betting'
            betConfirmed = document.getElementById('betconfirm') != null
        } else {
            currentStatus = 'ongoing'
        }
    }

    // Used for debugging in the popup
    matchStatusStorage.setMatchStatus(currentStatus, betConfirmed, loggedIn)

    return {
        currentStatus: currentStatus,
        betConfirmed: betConfirmed,
        loggedIn: loggedIn,
    }
}

/**
 * Get the match data from Salty Boy
 *
 * @returns {object} - Fighter data from : https://salty-boy.com/apidocs/#/default/get_current_match
 */
function getSaltyBoyMatchData() {
    verboseLog('Getting fighter data from SaltyBet.com')
    return fetch(`${SALTY_BOY_URL}/current-match`, { method: 'get' })
        .then((res) => res.json())
        .then((data) => {
            return data
        })
        .catch((err) => {
            console.error(
                'Something went wrong getting current match from server.',
                err
            )
            FETCH_FIGHTER_DATA = true
        })
}

/**
 * Places current bets
 *
 * @param {object} matchData - https://salty-boy.com/apidocs/#/default/get_current_match
 * @param {object} saltyBetStatus - Current state of Salty Bet
 * @returns
 */
function placeBets(matchData, saltyBetStatus) {
    verboseLog(`Calculating using betting algorithm ${BET_MODE}`)
    let betData = BET_MODES[BET_MODE](matchData)
    matchDataStorage.setCurrentMatchData(betData, matchData)
    FETCH_FIGHTER_DATA = false

    if (
        saltyBetStatus.currentStatus == 'ongoing' ||
        saltyBetStatus.loggedIn == false
    ) {
        return
    }

    if (ENABLE_BETTING == false) {
        return
    }

    let fighterRedBtn = document.getElementById('player1')
    let fighterBlueBtn = document.getElementById('player2')

    // Last sanity check
    if (
        fighterRedBtn.value != matchData.fighter_red ||
        fighterBlueBtn.value != matchData.fighter_blue
    ) {
        CURR_OUT_OF_DATE_ERR_COUNT += 1
        if (CURR_OUT_OF_DATE_ERR_COUNT > 5) {
            console.warn(
                'Current Match from server is out of date',
                fighterRedBtn.value,
                fighterBlueBtn.value,
                matchData
            )
        }

        FETCH_FIGHTER_DATA = true
        return
    }
    CURR_OUT_OF_DATE_ERR_COUNT = 0

    let wagerInput = document.getElementById('wager')

    let balance = parseInt(
        document.getElementById('balance').innerText.replaceAll(',', '')
    )
    if (matchData.match_format != 'tournament') {
        if (PREV_BALANCE != null) {
            winningsStorage.updateWinnings(balance - PREV_BALANCE)
        }
        PREV_BALANCE = balance
    }

    if (ENABLE_BETTING == false) {
        PREV_BALANCE = null
        return
    }

    wagerInput.value = getWagerAmount(
        balance,
        betData.confidence,
        matchData.match_format
    ).toString()
    if (betData.colour == 'red') {
        fighterRedBtn.click()
    } else {
        fighterBlueBtn.click()
    }

    verboseLog(
        `Betting on ${betData.colour} with a confidence of ${Math.round(
            betData.confidence
        )}`
    )
}

/**
 * Calculate the amount to wager
 *
 * @param {number} balance - Users balance, [0, ...]
 * @param {number} confidence - Confidence of the betting algorithm, [0, 1] or null
 * @param {*} match_format - Match format, should be one of "exhibition", "tournament", "matchmaking"
 * @returns
 */
function getWagerAmount(balance, confidence, match_format) {
    if (match_format == 'tournament' && ALL_IN_TOURNAMENTS == true) {
        verboseLog(
            'Detected tournament format and going all in on tournaments is set. So going all in.'
        )
        return balance
    }

    if (match_format == 'exhibition' && DOLLAR_EXHIBITIONS == true) {
        verboseLog(
            'Detected exhibition matches and dollar exhibitions set so only betting $1.'
        )
        return 1
    }

    if (ALL_IN_UNTIL != 0 && balance < ALL_IN_UNTIL) {
        verboseLog(
            `All in until is set (\$${ALL_IN_UNTIL}) and balance (\$${balance}) is less than the value therefore going all in.`
        )
        return balance
    }

    if (confidence == null) {
        verboseLog(
            'Betting method did not produce a confidence so only betting $1.'
        )
        return 1
    }

    // By default we use the entire balance
    let wagerAmount = balance * confidence

    let percentageBet = 0
    let amountBet = 0

    // If MAX_BET_PERCENTAGE is enabled we want to bet using this as the theoretical max
    if (MAX_BET_PERCENTAGE != 0) {
        percentageBet = wagerAmount * (MAX_BET_PERCENTAGE / 100)
    }

    // If MAX_BET_AMOUNT is enabled we want to bet using this as the theoretical max
    if (MAX_BET_AMOUNT != 0) {
        amountBet = Math.min(MAX_BET_AMOUNT, balance) * confidence
    }

    if (percentageBet != 0 && amountBet != 0) {
        // If both percentage and amount bets are enabled take the smallest
        verboseLog(
            `Both max bet amount set (\$${MAX_BET_AMOUNT}) and max bet percentage set (%${MAX_BET_PERCENTAGE}). Taking the lowest of both (\$${Math.round(
                percentageBet
            )}, \$${Math.round(amountBet)}).`
        )
        wagerAmount = Math.min(percentageBet, amountBet)
    } else if (percentageBet != 0) {
        // If only percentage is enabled take the percentage bet
        verboseLog(
            `Only max percentage percentage set (%${MAX_BET_PERCENTAGE}) using to determine bet amount.`
        )
        wagerAmount = percentageBet
    } else if (amountBet != 0) {
        // If only amount bet is enabled take the amount bet
        verboseLog(
            `Only max percentage amount set (\$${MAX_BET_AMOUNT}) using to determine bet amount.`
        )
        wagerAmount = amountBet
    }

    // Return the rounded amount to bet
    verboseLog(`Betting \$${Math.round(wagerAmount)}`)
    return Math.round(wagerAmount)
}

/**
 * Updates the bet settings as defined by user
 *
 * @param {object} betSettings
 */
function updateBetSettings(betSettings) {
    verboseLog('Detected bet settings updates')
    verboseLog(betSettings)

    // Update Bet Mode
    let betMode = betSettings.betMode
    if (betMode in BET_MODES) {
        BET_MODE = betMode
    } else {
        console.error(`Invalid bet mode ${betMode} detected.`)
    }

    // Update All In Until
    ALL_IN_UNTIL = betSettings.allInUntil

    // Update Max Bet Percentage
    MAX_BET_PERCENTAGE = betSettings.maxBetPercentage

    // Update Max Bet Amount
    MAX_BET_AMOUNT = betSettings.maxBetAmount

    // Update Tournament all in
    ALL_IN_TOURNAMENTS = betSettings.allInTournaments

    // Enable Betting
    ENABLE_BETTING = betSettings.enableBetting

    // Only $1 Exhibition Matches
    DOLLAR_EXHIBITIONS = betSettings.dollarExhibitions
}

/**
 * Updates debug settings for extension
 *
 * @param {object} debugSettings
 */
function updateDebugSettings(debugSettings) {
    DEBUG_ENABLED = debugSettings.debugEnabled

    verboseLog('Detected debug settings changes')
    verboseLog(debugSettings)
}

/**
 * Message to print to console if debug mode set
 *
 * @param {string} message
 */
function verboseLog(message) {
    if (DEBUG_ENABLED == false) {
        return
    }

    chrome.runtime.sendMessage({ message: message })
}

// Initialize the application
matchDataStorage
    .initializeCurrentMatchData()
    .then(() =>
        betSettingsStorage.initializeBetSettings(
            BET_MODE,
            ALL_IN_UNTIL,
            MAX_BET_PERCENTAGE,
            MAX_BET_AMOUNT,
            ALL_IN_TOURNAMENTS,
            ENABLE_BETTING,
            DOLLAR_EXHIBITIONS
        )
    )
    .then(() => matchStatusStorage.initializeMatchStatus())
    .then(() => winningsStorage.updateWinnings(0))
    .then(() => debugStorage.initializeDebugSettings())
    .then(() => debugStorage.getDebugSettings())
    .then((debugSettings) => {
        updateDebugSettings(debugSettings)
        return betSettingsStorage.getBetSettings()
    })
    .then((betSettings) => {
        updateBetSettings(betSettings)

        chrome.storage.onChanged.addListener((changes, namespace) => {
            if (namespace != 'local') {
                return
            }

            if ('betSettings' in changes) {
                updateBetSettings(changes.betSettings.newValue)
            }

            if ('debugSettings' in changes) {
                updateDebugSettings(changes.debugSettings.newValue)
            }
        })

        setInterval(run, RUN_INTERVAL)
    })
