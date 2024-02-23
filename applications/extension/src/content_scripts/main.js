// Storage Imports
import * as matchDataStorage from '../utils/storage/matchData.js'
import * as betSettingsStorage from '../utils/storage/betSettings.js'
import * as winningsStorage from '../utils/storage/winnings.js'
import * as matchStatusStorage from '../utils/storage/matchStatus.js'
import * as debugStorage from '../utils/storage/debugSettings.js'
import * as appSettingsStorage from '../utils/storage/appSettings.js'

// Betting Imports
import naiveBet from './bet_modes/naive.js'
import passiveBet from './bet_modes/passive.js'
import rngBet from './bet_modes/rng.js'
import eloTierBet from './bet_modes/eloTier.js'
import eloBet from './bet_modes/elo.js'

// Utility imports
import { calculateRedVsBlueMatchData } from '../utils/match.js'

const RUN_INTERVAL = 1000
const SALTY_BOY_URL = 'https://www.salty-boy.com'
const BET_MODES = {
    naive: naiveBet,
    passive: passiveBet,
    rng: rngBet,
    elo: eloBet,
    eloTier: eloTierBet,
}
const APP_VERSION = chrome.runtime.getManifest().version

// Bet Settings, values listed are defaults on init
let ALL_IN_UNTIL = 0
let MAX_BET_PERCENTAGE = 5
let MAX_BET_AMOUNT = 0
let BET_MODE = 'naive'
let ALL_IN_TOURNAMENTS = true
let ENABLE_BETTING = true
let EXHIBITION_BET = 1
let UPSET_MODE = false
let BET_TIER_X = true
let BET_TIER_S = true
let BET_TIER_A = true
let BET_TIER_B = true
let BET_TIER_P = true
let CONFIDENCE_THRESHOLD = 50

// Extension State Values
let LAST_STATUS = null
let FETCH_QUEUED = false
let FETCH_IN_PROGRESS = false
let FETCH_FIGHTER_DATA = true
let CURR_OUT_OF_DATE_ERR_COUNT = 0

// Balance Tracking
let PREV_BALANCE = null

// Debug Information
let DEBUG_ENABLED = false

// App Settings
let ENABLE_EXTENSION = true
let ENABLE_OVERLAY = true

const EXPECTED_LOCATION_RE = new RegExp(
    '^https?:\\/\\/(www\\.)?saltybet.com\\/?(\\?.+)?$'
)

/**
 * Main logic loop of the application.
 *
 * @returns
 */
function run() {
    if (expectedLocation() == false) {
        verboseLog('Not on the root path of SaltyBet doing nothing.')
        return
    }

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
            updateOverlay({}, true)
            updateBetOverlay({}, saltyBetStatus, true)

            // Give the Salty Boy server a few seconds to update
            if (FETCH_QUEUED == false) {
                verboseLog('Queue fetching of data from SaltyBoy in 5s.')
                setTimeout(() => {
                    verboseLog('Ready to fetch data SaltyBoy.')
                    FETCH_FIGHTER_DATA = true
                    FETCH_QUEUED = false
                }, 5000)
            }

            FETCH_QUEUED = true
        }

        if (
            LAST_STATUS != null &&
            LAST_STATUS.currentStatus == 'betting' &&
            saltyBetStatus.currentStatus == 'ongoing'
        ) {
            updateBetOverlay({}, saltyBetStatus, false)
        }

        LAST_STATUS = saltyBetStatus
    }

    if (FETCH_FIGHTER_DATA == false) {
        return
    }

    if (ENABLE_EXTENSION == false) {
        verboseLog(
            'Extension is disabled ensure the overlays are cleared and exit'
        )
        FETCH_FIGHTER_DATA = false
        updateOverlay({}, true)
        updateBetOverlay({}, saltyBetStatus, true)
        matchDataStorage.setCurrentMatchData({}, {})
        return
    }

    if (FETCH_IN_PROGRESS == true) {
        verboseLog('Fetch already in progress.')
        return
    }

    getSaltyBoyMatchData()
        .then((matchData) => {
            FETCH_IN_PROGRESS = false
            placeBets(matchData, saltyBetStatus)
            updateOverlay(matchData, false)
        })
        .catch((err) => {
            let err_message =
                'Something went wrong getting current match from server.'
            console.error(err_message, err)
            verboseLog(err_message)
            FETCH_FIGHTER_DATA = false
            FETCH_IN_PROGRESS = false
            if (saltyBetStatus.currentStatus == 'betting') {
                fallbackBet()
            }
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
    if (
        LAST_STATUS == null ||
        LAST_STATUS.currentStatus != currentStatus ||
        LAST_STATUS.betConfirmed != betConfirmed ||
        LAST_STATUS.loggedIn != loggedIn
    ) {
        matchStatusStorage.setMatchStatus(currentStatus, betConfirmed, loggedIn)
    }

    return {
        currentStatus: currentStatus,
        betConfirmed: betConfirmed,
        loggedIn: loggedIn,
    }
}

/**
 * Get the match data from Salty Boy
 *
 * @returns {object} - MatchData
 */
function getSaltyBoyMatchData() {
    FETCH_IN_PROGRESS = true

    function parseStats(fighterInfo) {
        if (fighterInfo == null) {
            return
        }

        let totalMatches = 0
        let wins = 0
        let totalBet = 0

        let fighterId = fighterInfo.id

        for (const match of fighterInfo.matches) {
            totalMatches += 1
            if (match.winner == fighterId) {
                wins += 1
            }
            if (match.fighter_red == fighterId) {
                totalBet += match.bet_red
            } else {
                totalBet += match.bet_blue
            }
        }

        let stats = {
            total_matches: 0,
            win_rate: 0.0,
            average_bet: 0.0,
        }

        if (totalMatches != 0) {
            stats.total_matches = totalMatches
            stats.win_rate = parseFloat((wins / totalMatches).toFixed(2))
            stats.average_bet = parseFloat((totalBet / totalMatches).toFixed(2))
        }

        fighterInfo['stats'] = stats
    }

    verboseLog('Getting fighter data from SaltyBoy')
    return fetch(
        `${SALTY_BOY_URL}/api/current_match_info/?saltyboy_version=${APP_VERSION}`,
        {
            method: 'get',
        }
    )
        .then((res) => res.json())
        .then((data) => {
            parseStats(data.fighter_blue_info)
            parseStats(data.fighter_red_info)
            return data
        })
}

/**
 * @returns {number} - Current balance
 */
function getBalance() {
    if (expectedLocation() == false) {
        return null
    }

    return parseInt(
        document.getElementById('balance').innerText.replaceAll(',', '')
    )
}

/**
 * Places current bets
 *
 * @param {object} matchData - MatchData
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

    let fighterRedBtn = document.getElementById('player1')
    let fighterBlueBtn = document.getElementById('player2')

    // Last sanity check
    if (
        fighterRedBtn.value != matchData.fighter_red ||
        fighterBlueBtn.value != matchData.fighter_blue
    ) {
        verboseLog('Match was out of date from server. Forcing a retry in 2s.')
        CURR_OUT_OF_DATE_ERR_COUNT += 1
        if (CURR_OUT_OF_DATE_ERR_COUNT > 5) {
            let warn_msg = 'Current Match from server is out of date'
            verboseLog(warn_msg)
            console.warn(
                warn_msg,
                fighterRedBtn.value,
                fighterBlueBtn.value,
                matchData
            )
            fallbackBet()
            return
        }

        setTimeout(() => {
            FETCH_FIGHTER_DATA = true
        }, 2000)

        return
    }
    CURR_OUT_OF_DATE_ERR_COUNT = 0

    updateBetOverlay(betData, saltyBetStatus, false)

    if (ENABLE_BETTING == false) {
        verboseLog('Betting is disabled do not bet.')
        PREV_BALANCE = null
        return
    }

    let wagerInput = document.getElementById('wager')

    let balance = getBalance()
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
        matchData.match_format,
        matchData.tier
    )

    if (wagerAmount != '') {
        wagerInput.value = wagerAmount.toString()

        let betColour = betData.colour

        if (UPSET_MODE == true) {
            verboseLog(
                `Upset mode enabled. Betting mode returned ${betData.colour} will bet opposite.`
            )
            if (betColour == 'red') {
                betColour = 'blue'
            } else {
                betColour = 'red'
            }
        }

        if (betColour == 'red') {
            fighterRedBtn.click()
        } else {
            fighterBlueBtn.click()
        }

        verboseLog(
            `Betting on ${betColour} with a confidence of ${
                Math.round(betData.confidence * 100) / 100
            }`
        )
    } else {
        verboseLog('Wager amount returned empty, not betting.')
    }
}

/**
 * @param {object} betData
 * @param {object} saltyBetStatus
 * @param {boolean} clear
 */
function updateBetOverlay(betData, saltyBetStatus, clear) {
    let confidenceSpanId = 'saltyboy-confidence-overlay'
    let confidenceSpan = document.getElementById(confidenceSpanId)

    if (ENABLE_OVERLAY == false) {
        verboseLog(
            'Overlay disabled. Removing betting overlay elements if they exist.'
        )
        if (confidenceSpan != null) {
            confidenceSpan.remove()
        }

        return
    }

    if (saltyBetStatus.currentStatus == 'ongoing') {
        verboseLog('Match ongoing removing confidence overlay.')
        if (confidenceSpan != null) {
            confidenceSpan.style.display = 'none'
        }

        return
    }

    if (clear == true) {
        verboseLog('Clearing confidence overlay.')
        if (confidenceSpan != null) {
            confidenceSpan.style.display = 'none'
        }
        return
    }

    verboseLog('Bets are open, updating confidence overlay.')

    if (confidenceSpan == null) {
        confidenceSpan = document.createElement('span')
        confidenceSpan.id = confidenceSpanId
        confidenceSpan.title =
            'Confidence from the betting algorithm in SaltyBoy.'
        confidenceSpan.style.cursor = 'help'
        let betTable = document.getElementById('bet-table')
        let menu = betTable.querySelector('.menu')
        menu.insertBefore(confidenceSpan, menu.firstChild)
    }

    confidenceSpan.style.display = 'block'
    confidenceSpan.innerText = `${Math.round(betData.confidence * 100)}%`

    if (betData.colour == 'red') {
        confidenceSpan.classList.add('redtext')
        confidenceSpan.classList.remove('bluetext')
    } else {
        confidenceSpan.classList.add('bluetext')
        confidenceSpan.classList.remove('redtext')
    }
}

/**
 *
 * @param {object} matchData - Match Data
 * @param {boolean} clearOverlay - Clear overlay between matches
 */
function updateOverlay(matchData, clearOverlay) {
    let bettingSpanIdBlue = 'saltyboy-betting-blue-overlay'
    let bettingSpanIdRed = 'saltyboy-betting-red-overlay'

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

    if (clearOverlay == true) {
        verboseLog('Overlay enabled. Clearing overlay between matches.')

        function clearBettingSpan(spanId) {
            let bettingSpan = document.getElementById(spanId)
            if (bettingSpan != null) {
                bettingSpan.innerText = 'Updating...'
            }
        }

        clearBettingSpan(bettingSpanIdRed)
        clearBettingSpan(bettingSpanIdBlue)

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
            bettingSpan.title =
                'Data derived from SaltyBoy. ELO (Tier ELO) | Win Rate | Matches Recorded | Wins against the other fighter if any.'
            bettingSpan.classList.add(classText)
            bettingSpan.style.fontSize = '0.9em'
            bettingSpan.style.marginTop = '12px'
            bettingSpan.style.display = 'inline-block'
            bettingSpan.style.width = '100%'
            bettingSpan.style.textAlign = 'center'
            bettingSpan.style.cursor = 'help'
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
 * @param {string} matchFormat - Match format, should be one of "exhibition", "tournament", "matchmaking"
 * @param {string} matchTier - Match tier, should be one of "X", "S", "A", "B", "P"
 * @returns
 */
function getWagerAmount(balance, confidence, matchFormat, matchTier) {
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

    if (matchFormat == 'matchmaking') {
        if (matchTier == 'X' && BET_TIER_X == false) {
            verboseLog('Disabled betting on X tier.')
            return ''
        }
        if (matchTier == 'S' && BET_TIER_S == false) {
            verboseLog('Disabled betting on S tier.')
            return ''
        }
        if (matchTier == 'A' && BET_TIER_A == false) {
            verboseLog('Disabled betting on A tier.')
            return ''
        }
        if (matchTier == 'B' && BET_TIER_B == false) {
            verboseLog('Disabled betting on B tier.')
            return ''
        }
        if (matchTier == 'P' && BET_TIER_P == false) {
            verboseLog('Disabled betting on P tier.')
            return ''
        }
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

    if (confidence * 100 < CONFIDENCE_THRESHOLD) {
        verboseLog(
            'Confidence is less than the confidence threshold betting $1'
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
        let err_message = `Invalid bet mode ${betMode} detected.`
        verboseLog(err_message)
        console.error(err_message)
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

    // Upset Mode
    UPSET_MODE = betSettings.upsetMode

    // Bet Tiers
    BET_TIER_X = betSettings.betTier.x
    BET_TIER_S = betSettings.betTier.s
    BET_TIER_A = betSettings.betTier.a
    BET_TIER_B = betSettings.betTier.b
    BET_TIER_P = betSettings.betTier.p

    // Confidence Threshold
    CONFIDENCE_THRESHOLD = Number(betSettings.confidenceThreshold)
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
    ENABLE_EXTENSION = appSettings.enableExtension
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

/**
 * Fallback bet to $1 on red in case server is out of date.
 */
function fallbackBet() {
    verboseLog('Fall back bet, betting $1 on red.')
    document.getElementById('wager').value = '1'
    document.getElementById('player1').click()
}

/**
 * Check if we are in the expected location
 */
function expectedLocation() {
    return window.location.toString().match(EXPECTED_LOCATION_RE) != null
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
            EXHIBITION_BET,
            UPSET_MODE,
            {
                x: BET_TIER_X,
                s: BET_TIER_S,
                a: BET_TIER_A,
                b: BET_TIER_B,
                p: BET_TIER_P,
            },
            CONFIDENCE_THRESHOLD
        )
    )
    .then(() => matchStatusStorage.initializeMatchStatus())
    .then(() => {
        PREV_BALANCE = getBalance()
        return winningsStorage.updateWinnings(0)
    })
    .then(() =>
        appSettingsStorage.initializeAppSettings(
            ENABLE_EXTENSION,
            ENABLE_OVERLAY
        )
    )
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
