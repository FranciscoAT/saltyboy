import * as matchDataStorage from '../utils/storage/matchData.js'
import * as betSettingsStorage from '../utils/storage/betSettings.js'
import * as winningsStorage from '../utils/storage/winnings.js'
import * as matchStatusStorage from '../utils/storage/matchStatus.js'

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
let FETCHED_FIGHTER_DATA = false
let CURR_OUT_OF_DATE_ERR_COUNT = 0

// BALANCE TRACKING
let PREV_BALANCE = null

/**
 * Main logic loop of the application.
 *
 * @returns
 */
function run() {
    let saltyBetStatus = getSaltyBetStatus()

    if (
        saltyBetStatus.currentStatus != 'betting' ||
        saltyBetStatus.betConfirmed == true ||
        FETCHED_FIGHTER_DATA == true
    ) {
        return
    }

    getSaltyBoyMatchData().then((matchData) => {
        placeBets(matchData)
    })
}

/**
 * Get the status of Salty Bet by reading elements from the DOM.
 *
 * @returns {object}
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

    let matchStatus = {
        currentStatus: currentStatus,
        betConfirmed: betConfirmed,
        loggedIn: loggedIn,
    }

    if (LAST_STATUS != matchStatus) {
        LAST_STATUS = matchStatus
        FETCHED_FIGHTER_DATA = false
    }

    return matchStatus
}

/**
 * Get the match data from Salty Boy
 *
 * @returns {object} - Fighter data from : https://salty-boy.com/apidocs/#/default/get_current_match
 */
function getSaltyBoyMatchData() {
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
            FETCHED_FIGHTER_DATA = false
        })
}

/**
 * Places current bets
 *
 * @param {object} matchData - https://salty-boy.com/apidocs/#/default/get_current_match
 * @returns
 */
function placeBets(matchData) {
    let wagerInput = document.getElementById('wager')
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
        return
    }
    CURR_OUT_OF_DATE_ERR_COUNT = 0

    let betData = BET_MODES[BET_MODE](matchData)
    let balance = parseInt(
        document.getElementById('balance').innerText.replaceAll(',', '')
    )
    if (matchData.match_format != 'tournament') {
        if (PREV_BALANCE != null) {
            updateStorageWinnings(balance - PREV_BALANCE)
        }
        PREV_BALANCE = balance
    }
    setStorageCurrentData(betData, matchData)

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
        return balance
    }

    if (match_format == 'exhibition' && DOLLAR_EXHIBITIONS == true) {
        return 1
    }

    if (ALL_IN_UNTIL != 0 && balance < ALL_IN_UNTIL) {
        return balance
    }

    if (confidence == null) {
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
        wagerAmount = Math.min(percentageBet, amountBet)
    } else if (percentageBet != 0) {
        // If only percentage is enabled take the percentage bet
        wagerAmount = percentageBet
    } else if (amountBet != 0) {
        // If only amount bet is enabled take the amount bet
        wagerAmount = amountBet
    }

    // Return the rounded amount to bet
    return Math.round(wagerAmount)
}

/**
 * Updates the bet settings as defined by user
 *
 * @param {object} betSettings
 */
function updateBetSettings(betSettings) {
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
    .then(() => betSettingsStorage.getBetSettings())
    .then((betSettings) => {
        updateBetSettings(betSettings)

        chrome.storage.onChanged.addListener((changes, namespace) => {
            if (namespace != 'local') {
                return
            }

            if ('betSettings' in changes) {
                updateBetSettings(changes.betSettings.newValue)
            }
        })

        setInterval(run, RUN_INTERVAL)
    })
