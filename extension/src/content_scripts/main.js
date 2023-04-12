import * as matchDataStorage from '../utils/storage/matchData.js'
import * as betSettingsStorage from '../utils/storage/betSettings.js'
import * as winningsStorage from '../utils/storage/winnings.js'
import * as matchStatusStorage from '../utils/storage/matchStatus.js'
import * as debugStorage from '../utils/storage/debugSettings.js'
import * as appSettingsStorage from '../utils/storage/appSettings.js'

// // Betting Imports
import naiveBet from './bet_modes/naive.js'
import passiveBet from './bet_modes/passive.js'
import rngBet from './bet_modes/rng.js'
import eloTierBet from './bet_modes/eloTier.js'
import eloBet from './bet_modes/elo.js'
import upsetBet from './bet_modes/upset.js'
import { calculateRedVsBlueMatchData } from '../utils/match.js'

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
let EXHIBITION_BET = 1

// Extension State Values
let LAST_STATUS = null
let FETCH_FIGHTER_DATA = true
let CURR_OUT_OF_DATE_ERR_COUNT = 0

// Balance Tracking
let PREV_BALANCE = null

// Debug Information
let DEBUG_ENABLED = false

// App Settings
let ENABLE_OVERLAY = true

/**
 * Main logic loop of the application.
 *
 * @returns
 */
function run() {
    let saltyBetStatus = getSaltyBetStatus()

    if (
        LAST_STATUS == null ||
        LAST_STATUS.currentStatus != saltyBetStatus.currentStatus ||
        LAST_STATUS.loggedIn != saltyBetStatus.loggedIn
    ) {
        verboseLog('Detected update in SaltyBet status.')
        verboseLog(saltyBetStatus)

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
        updateOverlay(matchData)
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
        verboseLog(
            'Either match is currently ongoing or we are not logged in. Will not bet.'
        )
        return
    }

    if (ENABLE_BETTING == false) {
        verboseLog('Betting is disabled do not bet.')
        PREV_BALANCE = null
        return
    }

    let fighterRedBtn = document.getElementById('player1')
    let fighterBlueBtn = document.getElementById('player2')

    // Last sanity check
    if (
        fighterRedBtn.value != matchData.fighter_red ||
        fighterBlueBtn.value != matchData.fighter_blue
    ) {
        verboseLog('Match was out of date from server. Forcing a retry.')
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
            verboseLog(
                `Detected a balance change of ${balance - PREV_BALANCE}$`
            )
            winningsStorage.updateWinnings(balance - PREV_BALANCE)
        }
        PREV_BALANCE = balance
    }

    let wagerAmount = getWagerAmount(
        balance,
        betData.confidence,
        matchData.match_format
    )

    if (wagerAmount != '') {
        wagerInput.value = wagerAmount.toString()
        if (betData.colour == 'red') {
            fighterRedBtn.click()
        } else {
            fighterBlueBtn.click()
        }

        verboseLog(
            `Betting on ${betData.colour} with a confidence of ${
                Math.round(betData.confidence * 100) / 100
            }`
        )
    } else {
        verboseLog('Wager amount returned empty, not betting.')
    }
}

/**
 *
 * @param {object} matchData - https://salty-boy.com/apidocs/#/default/get_current_match
 */
function updateOverlay(matchData) {
    let bettingSpanIdBlue = 'betting-blue-overlay'
    let bettingSpanIdRed = 'betting-red-overlay'

    if (ENABLE_OVERLAY == false) {
        verboseLog('Overlay disabled. Removing overlay elements if they exist.')
        function removeBettingSpan(spanId) {
            let bettingSpan = document.getElementById(spanId)
            if (bettingSpan != null) {
                bettingSpan.remove()
            }
        }

        removeBettingSpan(bettingSpanIdRed)
        removeBettingSpan(bettingSpanIdBlue)

        return
    }

    verboseLog(
        `Overlay enabled. Updating for ${matchData.fighter_red} vs ${matchData.fighter_blue}`
    )

    let fighterRed = document.getElementById('player1').value
    let fighterBlue = document.getElementById('player2').value

    if (
        fighterRed != matchData.fighter_red ||
        fighterBlue != matchData.fighter_blue
    ) {
        verboseLog('Match was out of date from server. Not updating overlay.')
        return
    }

    function updateForPlayer(
        fighterSubmitBtnId,
        spanId,
        classText,
        fighterInfo
    ) {
        let bettingSpan = document.getElementById(spanId)
        if (bettingSpan == null) {
            bettingSpan = document.createElement('span')
            bettingSpan.id = spanId
            bettingSpan.classList.add(classText)
            bettingSpan.style.fontSize = '0.9em'
            bettingSpan.style.marginTop = '12px'
            bettingSpan.style.display = 'inline-block'
            bettingSpan.style.width = '100%'
            bettingSpan.style.textAlign = 'center'
            document
                .getElementById(fighterSubmitBtnId)
                .parentNode.appendChild(bettingSpan)
        }

        if (matchData.match_format == 'exhibition') {
            bettingSpan.innerText = 'Exhibition match'
            return
        }

        let redVsBlueInfo = calculateRedVsBlueMatchData(
            matchData.fighter_red_info?.matches,
            matchData.fighter_red_info?.id,
            matchData.fighter_blue_info?.id
        )

        let winsVs = 0
        if (fighterSubmitBtnId == 'player1') {
            winsVs = redVsBlueInfo.redWinsVsBlue
        } else {
            winsVs =
                redVsBlueInfo.redMatchesVsBlue - redVsBlueInfo.redWinsVsBlue
        }

        bettingSpan.innerText = `ELO (T): ${fighterInfo.elo} (${
            fighterInfo.tier_elo
        }) | WR: ${Math.round(fighterInfo.stats.win_rate * 100)}% | Matches: ${
            fighterInfo.stats.total_matches
        } | Wins VS: ${winsVs}`
    }

    updateForPlayer(
        'player1',
        bettingSpanIdRed,
        'redtext',
        matchData.fighter_red_info
    )
    updateForPlayer(
        'player2',
        bettingSpanIdBlue,
        'bluetext',
        matchData.fighter_blue_info
    )
}

/**
 * Calculate the amount to wager
 *
 * @param {number} balance - Users balance, [0, ...]
 * @param {number} confidence - Confidence of the betting algorithm, [0, 1] or null
 * @param {*} matchFormat - Match format, should be one of "exhibition", "tournament", "matchmaking"
 * @returns
 */
function getWagerAmount(balance, confidence, matchFormat) {
    if (matchFormat == 'tournament' && ALL_IN_TOURNAMENTS == true) {
        verboseLog(
            'Detected tournament format and going all in on tournaments is set. So going all in.'
        )
        return balance
    }

    if (matchFormat == 'exhibition') {
        if (EXHIBITION_BET == 0) {
            verboseLog(
                'Detected exhibition matches and exhibition bet set to $0, not betting.'
            )
            return ''
        }

        verboseLog(
            `Detected exhibition betting exhibition bet amount \$${EXHIBITION_BET}`
        )

        return EXHIBITION_BET
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
    ALL_IN_UNTIL = Number(betSettings.allInUntil)

    // Update Max Bet Percentage
    MAX_BET_PERCENTAGE = Number(betSettings.maxBetPercentage)

    // Update Max Bet Amount
    MAX_BET_AMOUNT = Number(betSettings.maxBetAmount)

    // Update Tournament all in
    ALL_IN_TOURNAMENTS = betSettings.allInTournaments

    // Enable Betting
    ENABLE_BETTING = betSettings.enableBetting

    // Amount to bet on Exhibitions
    EXHIBITION_BET = Number(betSettings.exhibitionBet)
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
 * Updates app settings
 *
 * @param {object} appSettings
 */
function updateAppSettings(appSettings) {
    ENABLE_OVERLAY = appSettings.enableOverlay

    verboseLog('Detecting app settings changes')
    verboseLog(appSettings)

    // Force a refetching of data
    FETCH_FIGHTER_DATA = true
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
            EXHIBITION_BET
        )
    )
    .then(() => matchStatusStorage.initializeMatchStatus())
    .then(() => winningsStorage.updateWinnings(0))
    .then(() => appSettingsStorage.initializeAppSettings(ENABLE_OVERLAY))
    .then(() => appSettingsStorage.getAppSettings())
    .then((appSettings) => {
        updateAppSettings(appSettings)
        return debugStorage.initializeDebugSettings()
    })
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

            if ('appSettings' in changes) {
                updateAppSettings(changes.appSettings.newValue)
            }
        })

        chrome.runtime.onMessage.addListener(
            (request, sender, sendResponse) => {
                if ('reBet' in request) {
                    verboseLog('Manual re-bet received.')
                    let wagerInput = document.getElementById('wager')
                    if (wagerInput.style.display != 'none') {
                        wagerInput.value = ''
                    }
                    FETCH_FIGHTER_DATA = true
                }
            }
        )

        setInterval(run, RUN_INTERVAL)
    })
