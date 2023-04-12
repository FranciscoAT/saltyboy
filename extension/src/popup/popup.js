import { calculateRedVsBlueMatchData } from '../utils/match'

import * as matchDataStorage from '../utils/storage/matchData.js'
import * as betSettingsStorage from '../utils/storage/betSettings.js'
import * as winningsStorage from '../utils/storage/winnings.js'
import * as matchStatusStorage from '../utils/storage/matchStatus.js'
import * as debugStorage from '../utils/storage/debugSettings.js'
import * as appSettingsStorage from '../utils/storage/appSettings.js'

// TODO: tournament span id is tournament-note
// Debug Info
let debugInfoTitle = document.getElementById('debug-info-title')
let loggedIn = document.getElementById('logged-in')
let statusSpan = document.getElementById('match-status')
let lastUpdated = document.getElementById('last-updated')
let betConfirmed = document.getElementById('bet-confirmed')
let version = document.getElementById('version')
let alertLocalStorageBtn = document.getElementById('alert-storage')
let debugEnabled = document.getElementById('debug-enabled')

// Bet Settings
let allInUntil = document.getElementById('all-in-until')
let maxBetPercentage = document.getElementById('max-bet-percentage')
let maxBetAmount = document.getElementById('max-bet-amount')
let betMode = document.getElementById('bet-mode')
let enableBetting = document.getElementById('enable-betting')
let allInTournaments = document.getElementById('all-in-tournaments')
let dollarExhibitions = document.getElementById('dollar-exhibitions')
let betModeTitle = document.getElementById('bet-mode-title')
let reBetBtn = document.getElementById('re-bet-btn')

// App Settings
let enableOverlay = document.getElementById('enable-overlay')

// Current Bet Data
let matchTable = document.getElementById('match-table')
let headToHead = document.getElementById('head-to-head')
let tieredElo = document.getElementById('tiered-elo')
let currentBetConfidence = document.getElementById('bet-confidence')
let currentBetColour = document.getElementById('bet-colour')
let redFighter = document.getElementById('red-fighter')
let blueFighter = document.getElementById('blue-fighter')
let matchMode = document.getElementById('match-mode')
let matchTier = document.getElementById('match-tier')
let redMatches = document.getElementById('red-matches')
let redWinRate = document.getElementById('red-win-rate')
let redElo = document.getElementById('red-elo')
let redTierElo = document.getElementById('red-tier-elo')
let redHeadToHead = document.getElementById('red-head-to-head')
let blueMatches = document.getElementById('blue-matches')
let blueWinRate = document.getElementById('blue-win-rate')
let blueElo = document.getElementById('blue-elo')
let blueTierElo = document.getElementById('blue-tier-elo')
let blueHeadToHead = document.getElementById('blue-head-to-head')

// Session Data
let totalWinnings = document.getElementById('total-winnings')
let sessionWinnings = document.getElementById('session-winnings')
let resetSessionWinningsBtn = document.getElementById('reset-session-winnings')

const MISSING = '-'
const BET_MODE_INFO = {
    naive: 'Naive betting using a combination of win-rates from past matches, breaking ties with average bet amounts. Will always bet $1 on red if no past matches are recorded for either fighter. Always bets $1 on red in exhibitions. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/naive.js">Source</a>)',
    passive:
        'Passive betting just bets $1 on Red. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/passive.js">Source</a>)',
    rng: 'Flips a coin to determine if betting for Red or Blue. Then goes all in. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/rng.js">Source</a>)',
    elo: 'Bets using ELO of the fighters. Fighters start at 1500 ELO and use a K value of 32. Breaks ties using average bet. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/elo.js">Source</a>)',
    eloTier:
        'Bets using the Tiered ELO of the fighters. Whenever a Fighter changes tier they go to 1500 tiered ELO and use a K value of 32. Breaks ties using average bet. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/eloTier.js">Source</a>)',
    upset: 'A reversed method of naive but flips the end result to the fighter who should lose instead of win. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/upset.js">Source</a>)',
}

function updateStatus(matchStatus) {
    loggedIn.innerText = matchStatus.loggedIn
    betConfirmed.innerText = matchStatus.betConfirmed
    statusSpan.innerText = matchStatus.currentStatus
    lastUpdated.innerText = new Date().toString()

    resize()
}

function toggleSection(identifier) {
    let contentWrapper = document.getElementById(`${identifier}-content`)
    let showHideSymbol = document.getElementById(`${identifier}-symbol`)

    if (showHideSymbol.innerText == '+') {
        contentWrapper.classList.remove('hidden')
        showHideSymbol.innerText = '-'
    } else {
        contentWrapper.classList.add('hidden')
        showHideSymbol.innerText = '+'
    }

    resize()
}

function updateBetModeInfo(selectedMode) {
    let betModeInfoPTag = document.getElementById('bet-mode-info')
    let betModeInfo = BET_MODE_INFO[selectedMode]

    if (betModeInfo == null) {
        betModeInfoPTag.innerText = 'Invalid bet mode selected'
    } else {
        betModeInfoPTag.innerHTML = betModeInfo
    }
}

function updateBetSettings() {
    betSettingsStorage.setBetSettings(
        betMode.value,
        allInUntil.value,
        maxBetPercentage.value,
        maxBetAmount.value,
        allInTournaments.checked,
        enableBetting.checked,
        dollarExhibitions.checked
    )

    updateBetModeInfo(betMode.value)

    resize()
}

function updateCurrentData(currentData) {
    if (currentData != null) {
        if (currentData.confidence == null) {
            currentBetConfidence.innerText = 'Unable to determine'
        } else {
            currentBetConfidence.innerText = `${Math.round(
                currentData.confidence * 100
            )}%`
        }

        currentBetColour.innerText = currentData.inFavourOf
        if (currentData.inFavourOf == 'red') {
            currentBetColour.classList.add('red')
            currentBetColour.classList.remove('blue')
        } else {
            currentBetColour.classList.add('blue')
            currentBetColour.classList.remove('red')
        }

        if (currentData.red != null || currentData.blue != null) {
            updateCurrentMatchTable(currentData)
            matchTable.classList.remove('hidden')
        } else {
            matchTable.classList.add('hidden')
        }

        redFighter.innerText = currentData.red.name
        blueFighter.innerText = currentData.blue.name

        matchMode.innerText = currentData.mode
        matchTier.innerText = currentData.tier
    } else {
        currentBetConfidence.innerText = 'No current bet'
        currentBetColour.innerText = 'No current bet'

        currentBetColour.classList.remove('red')
        currentBetColour.classList.remove('blue')

        redFighter.innerText = 'Unknown'
        blueFighter.innerText = 'Unknown'

        matchMode.innerText = 'Unknown'
        matchTier.innerText = 'Unknown'
    }

    resize()
}

function updateCurrentMatchTable(currentData) {
    redMatches.innerText = currentData.red?.totalMatches ?? MISSING
    redWinRate.innerText = currentData.red?.winRate ?? MISSING
    redElo.innerText = currentData.red?.elo ?? MISSING

    blueMatches.innerText = currentData.blue?.totalMatches ?? MISSING
    blueWinRate.innerText = currentData.blue?.winRate ?? MISSING
    blueElo.innerText = currentData.blue?.elo ?? MISSING

    let shouldShowTieredElo =
        currentData.red?.elo !== currentData.red?.tierElo ||
        currentData.blue?.elo !== currentData.blue?.tierElo
    if (shouldShowTieredElo) {
        redTierElo.innerText = currentData.red?.tierElo ?? MISSING
        blueTierElo.innerText = currentData.blue?.tierElo ?? MISSING
        tieredElo.classList.remove('hidden')
    } else {
        tieredElo.classList.add('hidden')
    }

    if (currentData.matches != null || currentData.matches != undefined) {
        let redVsBlueMatchData = calculateRedVsBlueMatchData(
            currentData.matches,
            currentData.red?.id,
            currentData.blue?.id
        )
        if (redVsBlueMatchData.redMatchesVsBlue != 0) {
            let redWins = redVsBlueMatchData.redWinsVsBlue
            let blueWins = redVsBlueMatchData.redMatchesVsBlue - redWins
            redHeadToHead.innerText = redWins.toString()
            blueHeadToHead.innerText = blueWins.toString()
            headToHead.classList.remove('hidden')
        } else {
            headToHead.classList.add('hidden')
        }
    } else {
        headToHead.classList.add('hidden')
    }
}

function updateWinningSpan(amount, span) {
    if (amount == null) {
        amount = 0
    }

    let strAmount = Math.abs(amount).toLocaleString()
    if (amount < 0) {
        span.innerText = `-\$${strAmount}`
        span.classList.add('red')
        span.classList.remove('green')
    } else {
        span.innerText = `\$${strAmount}`
        span.classList.add('green')
        span.classList.remove('red')
    }
}

function updateWinnings(winnings) {
    if (winnings == null) {
        // Initial state of application
        winnings = {
            total: 0,
            session: 0,
        }
    }
    updateWinningSpan(winnings.total, totalWinnings)
    updateWinningSpan(winnings.session, sessionWinnings)

    resize()
}

function resize() {
    let wrapper = document.getElementById('wrapper')
    document.body.parentNode.style.height = `${wrapper.clientHeight}px`
}

function alertLocalStorage() {
    chrome.storage.local.get(
        [
            'betSettings',
            'matchStatus',
            'winnings',
            'debugSettings',
            'appSettings',
        ],
        (localStorage) => {
            alert(JSON.stringify(localStorage, null, 2))
        }
    )
}

function updateDebug(debugSettings) {
    debugEnabled.checked = debugSettings.debugEnabled
}

function updateDebugSettings() {
    debugStorage.setDebugSettings(debugEnabled.checked)
}

function updateAppSettings() {
    appSettingsStorage.setAppSettings(enableOverlay.checked)
}

// Sync bet settings on popup load
betSettingsStorage.getBetSettings().then((betSettings) => {
    allInUntil.value = betSettings.allInUntil
    maxBetPercentage.value = betSettings.maxBetPercentage
    maxBetAmount.value = betSettings.maxBetAmount
    enableBetting.checked = betSettings.enableBetting
    betMode.value = betSettings.betMode
    allInTournaments.checked = betSettings.allInTournaments
    dollarExhibitions.checked = betSettings.dollarExhibitions
    updateBetModeInfo(betSettings.betMode)
})

// Sync app settings
appSettingsStorage.getAppSettings().then((appSettings) => {
    enableOverlay.checked = appSettings.enableOverlay
})

// Sync match status on popup load
matchStatusStorage.getMatchStatus().then((matchStatus) => {
    updateStatus(matchStatus)
})

// Sync current match data
matchDataStorage.getCurrentMatchData().then((currentData) => {
    updateCurrentData(currentData)
})

// Sync Winnings
winningsStorage.getWinnings().then((winnings) => {
    updateWinnings(winnings)
})

// Sync Debug information
debugStorage.getDebugSettings().then((debugSettings) => {
    updateDebug(debugSettings)
})

chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace != 'local') {
        return
    }

    if ('matchStatus' in changes) {
        updateStatus(changes.matchStatus.newValue)
    }

    if ('currentData' in changes) {
        updateCurrentData(changes.currentData.newValue)
    }

    if ('winnings' in changes) {
        updateWinnings(changes.winnings.newValue)
    }
})

// Initialize Bet Setting Changes Listeners
betMode.addEventListener('change', updateBetSettings)
allInUntil.addEventListener('change', updateBetSettings)
maxBetPercentage.addEventListener('change', updateBetSettings)
maxBetAmount.addEventListener('change', updateBetSettings)
enableBetting.addEventListener('change', updateBetSettings)
allInTournaments.addEventListener('change', updateBetSettings)
dollarExhibitions.addEventListener('change', updateBetSettings)

debugInfoTitle.addEventListener('click', () => {
    toggleSection('debug-info')
})
betModeTitle.addEventListener('click', () => {
    toggleSection('bet-mode')
})

toggleSection('bet-mode')

resetSessionWinningsBtn.addEventListener('click', () => {
    winningsStorage.resetSessionWinnings()
})

alertLocalStorageBtn.addEventListener('click', () => {
    alertLocalStorage()
})

debugEnabled.addEventListener('change', updateDebugSettings)

enableOverlay.addEventListener('change', updateAppSettings)

reBetBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ reBet: true })
})

version.innerText = chrome.runtime.getManifest().version

window.onload = resize
