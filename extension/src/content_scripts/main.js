import {
    setStorageMatchStatus,
    setStorageBetSettings,
    getStorageBetSettings,
    setStorageCurrentBetData,
    updateStorageWinnings,
} from '../utils/storage.js'
import naiveBet from './bet_modes/naive.js'
import passiveBet from './bet_modes/passive.js'
import rngBet from './bet_modes/rng.js'
import eloTierBet from './bet_modes/eloTier.js'
import eloBet from './bet_modes/elo.js'

const RUN_INTERVAL = 5000
const SALTY_BOY_URL = 'https://www.salty-boy.com'
const BET_MODES = {
    naive: naiveBet,
    passive: passiveBet,
    rng: rngBet,
    elo: eloBet,
    eloTier: eloTierBet,
}

// Bet Settings, values listed are defaults on init
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

function run() {
    if (ENABLE_BETTING == false) {
        PREV_BALANCE = null
        return
    }
    let matchStatus = updateStatus()
    if (matchStatus.loggedIn == false) {
        return
    }
    getFighterData(matchStatus)
}

function updateStatus() {
    let betStatus = document.getElementsById("betstatus")

    let currentStatus = 'unknown'
    let loggedIn = document.getElementById("rank") != null
    let betConfirmed = false

    if (loggedIn) {
        if (betStatus.innerText == "Bets are OPEN!") {
            currentStatus = "betting"
            betConfirmed = document.getElementById('betconfirm') != null
        } else {
            currentStatus = "ongoing"
        }
    }

    setStorageMatchStatus(currentStatus, betConfirmed, loggedIn)

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

function getFighterData(matchStatus) {
    if (
        matchStatus.currentStatus != 'betting' ||
        matchStatus.betConfirmed == true ||
        FETCHED_FIGHTER_DATA == true
    ) {
        return
    }

    FETCHED_FIGHTER_DATA = true

    fetch(`${SALTY_BOY_URL}/current-match`, { method: 'get' })
        .then((res) => res.json())
        .then((data) => {
            placeBets(data)
        })
        .catch((err) => {
            console.error(
                'Something went wrong getting current match from server.',
                err
            )
            FETCHED_FIGHTER_DATA = false
        })
}

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
        document.getElementById('balance').innerText.replace(',', '')
    )
    if (matchData.match_format != 'tournament') {
        if (PREV_BALANCE != null) {
            updateStorageWinnings(balance - PREV_BALANCE)
        }
        PREV_BALANCE = balance
    }
    setStorageCurrentBetData(betData.confidence, betData.colour)
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

function getWagerAmount(balance, confidence, match_format) {
    if (match_format == 'tournament' && ALL_IN_TOURNAMENTS == true) {
        return balance
    }

    if (match_format == 'exhibition' && DOLLAR_EXHIBITIONS == true) {
        return 1
    }

    if (confidence == null) {
        return 1
    }

    let percentageBet = 0
    let amountBet = 0
    let wagerAmount = balance * confidence

    if (MAX_BET_PERCENTAGE != 0) {
        percentageBet = balance * confidence * (MAX_BET_PERCENTAGE / 100)
    }

    if (MAX_BET_AMOUNT != 0) {
        if (MAX_BET_AMOUNT > balance) {
            amountBet = balance * confidence
        } else {
            amountBet = MAX_BET_AMOUNT * confidence
        }
    }

    if (percentageBet != 0 && amountBet != 0) {
        wagerAmount = Math.min(percentageBet, amountBet)
    } else if (percentageBet != 0) {
        wagerAmount = percentageBet
    } else if (amountBet != 0) {
        wagerAmount = amountBet
    }

    return Math.round(wagerAmount)
}

function updateBetSettings(betSettings) {
    // Update Bet Mode
    let betMode = betSettings.betMode
    if (betMode in BET_MODES) {
        BET_MODE = betMode
    } else {
        console.error(`Invalid bet mode ${betMode} detected.`)
    }

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

getStorageBetSettings()
    .then((betSettings) => {
        let updateDefaults = false
        if (betSettings == null) {
            betSettings = {
                betMode: BET_MODE,
                maxBetPercentage: MAX_BET_PERCENTAGE,
                maxBetAmount: MAX_BET_AMOUNT,
                allInTournaments: ALL_IN_TOURNAMENTS,
                enableBetting: ENABLE_BETTING,
                dollarExhibitions: DOLLAR_EXHIBITIONS,
            }
        } else {
            if (betSettings.betMode == null) {
                updateDefaults = true
                betSettings.betMode = BET_MODE
            }
            if (betSettings.maxBetAmount == null) {
                updateDefaults = true
                betSettings.maxBetAmount = MAX_BET_AMOUNT
            }
            if (betSettings.maxBetPercentage == null) {
                updateDefaults = true
                betSettings.maxBetPercentage = MAX_BET_PERCENTAGE
            }
            if (betSettings.allInTournaments == null) {
                updateDefaults = true
                betSettings.allInTournaments = ALL_IN_TOURNAMENTS
            }

            if (betSettings.enableBetting == null) {
                updateDefaults = true
                betSettings.enableBetting = ENABLE_BETTING
            }

            if (betSettings.dollarExhibitions == null) {
                updateDefaults = true
                betSettings.dollarExhibitions = DOLLAR_EXHIBITIONS
            }
        }

        if (updateDefaults == true) {
            setStorageBetSettings(
                betSettings.betMode,
                betSettings.maxBetPercentage,
                betSettings.maxBetAmount,
                betSettings.allInTournaments,
                betSettings.enableBetting,
                betSettings.dollarExhibitions
            )
        }
        updateBetSettings(betSettings)
    })
    .catch((err) => {
        console.error(
            `Failed to properly update bet settings into extension storage. ${err}`
        )
    })

chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace != 'local') {
        return
    }

    if ('betSettings' in changes) {
        updateBetSettings(changes.betSettings.newValue)
    }
})

setInterval(run, RUN_INTERVAL)
