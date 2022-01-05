import {
    getStorageBetSettings,
    setStorageBetSettings,
    getStorageMatchStatus,
    getStorageCurrentBetData,
    getStorageWinnings,
    resetStorageSessionWinnings,
} from '../utils/storage'

// Debug Info
let debugInfoTitle = document.getElementById('debug-info-title')
let loggedIn = document.getElementById('logged-in')
let statusSpan = document.getElementById('match-status')
let lastUpdated = document.getElementById('last-updated')
let betConfirmed = document.getElementById('bet-confirmed')

// Bet Settings
let maxBetPercentage = document.getElementById('max-bet-percentage')
let maxBetAmount = document.getElementById('max-bet-amount')
let betMode = document.getElementById('bet-mode')
let enableBetting = document.getElementById('enable-betting')
let allInTournaments = document.getElementById('all-in-tournaments')
let dollarExhibitions = document.getElementById('dollar-exhibitions')
let betModeTitle = document.getElementById('bet-mode-title')

// Other
let version = document.getElementById('version')

// Current Bet Data
let currentBetConfidence = document.getElementById('bet-confidence')
let currentBetColour = document.getElementById('bet-colour')

// Session Data
let totalWinnings = document.getElementById('total-winnings')
let sessionWinnings = document.getElementById('session-winnings')
let resetSessionWinningsBtn = document.getElementById('reset-session-winnings')

const BET_MODE_INFO = {
    naive: 'Naive betting using a combination of win-rates from past matches, breaking ties with average bet amounts. Will always bet $1 on red if no past matches are recorded for either fighter. Always bets $1 on red in exhibitions. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/naive.js">Source</a>)',
    passive:
        'Passive betting just bets $1 on Red. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/passive.js">Source</a>)',
    rng: 'Flips a coin to determine if betting for Red or Blue. Then goes all in. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/rng.js">Source</a>)',
    elo: 'Bets using ELO of the fighters. Fighters start at 1500 ELO and use a K value of 32. Breaks ties using average bet. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/elo.js">Source</a>)',
    eloTier:
        'Bets using the Tiered ELO of the fighters. Whenever a Fighter changes tier they go to 1500 tiered ELO and use a K value of 32. Breaks ties using average bet. (<a href="https://github.com/FranciscoAT/saltyboy/blob/master/extension/src/content_scripts/bet_modes/eloTier.js">Source</a>)',
}

function updateStatus(matchStatus) {
    loggedIn.innerText = matchStatus.loggedIn
    betConfirmed.innerText = matchStatus.betConfirmed
    statusSpan.innerText = matchStatus.currentStatus
    lastUpdated.innerText = new Date().toString()
}

function toggleSection(identifier) {
    let contentWrapper = document.getElementById(`${identifier}-content`)
    let showHideSymbol = document.getElementById(`${identifier}-symbol`)

    if (showHideSymbol.innerText == '+') {
        contentWrapper.style.display = 'block'
        showHideSymbol.innerText = '-'
    } else {
        contentWrapper.style.display = 'none'
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

    resize()
}

function updateBetSettings() {
    setStorageBetSettings(
        betMode.value,
        maxBetPercentage.value,
        maxBetAmount.value,
        allInTournaments.checked,
        enableBetting.checked,
        dollarExhibitions.checked
    )
    updateBetModeInfo(betMode.value)
}

function updateCurrentBetData(currentBetData) {
    if (currentBetData != null) {
        if (currentBetData.confidence == null) {
            currentBetConfidence.innerText = 'Unable to determine'
        } else {
            currentBetConfidence.innerText = `${Math.round(
                currentBetData.confidence * 100
            )}%`
        }
        currentBetColour.innerText = currentBetData.inFavourOf
        if (currentBetData.inFavourOf == 'red') {
            currentBetColour.classList.add('bet-colour-red')
            currentBetColour.classList.remove('bet-colour-blue')
        } else {
            currentBetColour.classList.add('bet-colour-blue')
            currentBetColour.classList.remove('bet-colour-red')
        }
    } else {
        currentBetConfidence.innerText = 'No current bet'
        currentBetColour.innerText = 'No current bet'
        currentBetColour.classList.remove('bet-colour-red')
        currentBetColour.classList.remove('bet-colour-blue')
    }
}

function updateWinningSpan(amount, span) {
    if (amount == null) {
        amount = 0
    }
    if (amount < 0) {
        span.innerText = `-\$${Math.abs(amount)}`
        span.classList.add('winnings-colour-red')
        span.classList.remove('winnings-colour-green')
    } else {
        span.innerText = `\$${amount}`
        span.classList.add('winnings-colour-green')
        span.classList.remove('winnings-colour-red')
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
}

function resize() {
    let wrapper = document.getElementById('wrapper')
    document.body.parentNode.style.height = `${wrapper.clientHeight}px`
}

// Sync bet settings on popup load
getStorageBetSettings().then((betSettings) => {
    maxBetPercentage.value = betSettings.maxBetPercentage
    maxBetAmount.value = betSettings.maxBetAmount
    enableBetting.checked = betSettings.enableBetting
    betMode.value = betSettings.betMode
    allInTournaments.checked = betSettings.allInTournaments
    dollarExhibitions.checked = betSettings.dollarExhibitions
    updateBetModeInfo(betSettings.betMode)
})

// Sync match status on popup load
getStorageMatchStatus().then((matchStatus) => {
    updateStatus(matchStatus)
})

getStorageCurrentBetData().then((currentBetData) => {
    updateCurrentBetData(currentBetData)
})

// Sync Winnings
getStorageWinnings().then((winnings) => {
    updateWinnings(winnings)
})

chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace != 'local') {
        return
    }

    if ('matchStatus' in changes) {
        updateStatus(changes.matchStatus.newValue)
    }

    if ('currentBetData' in changes) {
        updateCurrentBetData(changes.currentBetData.newValue)
    }

    if ('winnings' in changes) {
        updateWinnings(changes.winnings.newValue)
    }
})

// Initialize Bet Setting Changes Listeners
betMode.addEventListener('change', updateBetSettings)
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

resetSessionWinningsBtn.addEventListener('click', () => {
    resetStorageSessionWinnings()
})

version.innerText = chrome.runtime.getManifest().version

resize()
