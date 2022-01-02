import {
    getStorageBetSettings,
    setStorageBetSettings,
    getStorageMatchStatus,
} from '../utils/storage'


// Debug Info
let debugInfoToggle = document.getElementById('debug-info-title')
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

const BET_MODE_INFO = {
    naive: 'Naive betting using a combination of win-rates from past matches, breaking ties with average bet amounts. Will always bet $1 on red if no past matches are recorded for either fighter. Never bets in exhibitions. For more info see: <a href="https://github.com/FranciscoAT/extension/src/content_scripts/bet_modes/naive.js">naive.js</a>',
}

function updateStatus(matchStatus) {
    loggedIn.innerText = matchStatus.loggedIn
    betConfirmed.innerText = matchStatus.betConfirmed
    statusSpan.innerText = matchStatus.currentStatus
    lastUpdated.innerText = new Date().toString()
}

function toggleDebug() {
    let debugInfoDiv = document.getElementById('debug-info')
    let showHideSymbol = document.getElementById('show-hide-symbol')

    if (showHideSymbol.innerText == '+') {
        debugInfoDiv.style.display = 'block'
        showHideSymbol.innerText = '-'
    } else {
        debugInfoDiv.style.display = 'none'
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
        enableBetting.checked
    )
    updateBetModeInfo(betMode.value)
}

function resize() {
    let wrapper = document.getElementById("wrapper")
    document.body.parentNode.style.height = `${wrapper.clientHeight}px`;
}

// Sync bet settings on popup load
getStorageBetSettings().then((betSettings) => {
    maxBetPercentage.value = betSettings.maxBetPercentage
    maxBetAmount.value = betSettings.maxBetAmount
    enableBetting.checked = betSettings.enableBetting
    betMode.value = betSettings.betMode
    allInTournaments.checked = betSettings.allInTournaments
    updateBetModeInfo(betMode.value)
})

// Sync match status on popup load
getStorageMatchStatus().then((matchStatus) => {
    updateStatus(matchStatus)
})

chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace != 'local') {
        return
    }

    if ('matchStatus' in changes) {
        updateStatus(changes.matchStatus.newValue)
    }
})

// Initialize Bet Setting Changes Listeners
betMode.addEventListener('change', updateBetSettings)
maxBetPercentage.addEventListener('change', updateBetSettings)
maxBetAmount.addEventListener('change', updateBetSettings)
enableBetting.addEventListener('change', updateBetSettings)
allInTournaments.addEventListener('change', updateBetSettings)

debugInfoToggle.addEventListener('click', toggleDebug)

resize()
