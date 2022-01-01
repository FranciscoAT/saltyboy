import naiveBet from './bet_modes/naive.js'

const RUN_INTERVAL = 5000
const SALTY_BOY_URL = 'https://www.salty-boy.com'
const BET_MODES = {
    naive: naiveBet,
}

let MAX_BET_PERCENTAGE = 0.05 // TODO: allow this to be configurable
let BET_MODE = 'naive'
let LAST_STATUS = null
let FETCHED_FIGHTER_DATA = false
let CURR_OUT_OF_DATE_ERR_COUNT = 0

function run() {
    let status = updateStatus()
    if (status['loggedIn'] == false) {
        return
    }
    getFighterData(status)
}

function updateStatus() {
    let loggedIn = document.getElementsByClassName('nav-text').length == 0
    let odds = document.getElementById('odds')
    let matchStatus = 'unknown'
    let betConfirmed = false

    if (loggedIn) {
        if (
            odds.getInnerHTML() == '' ||
            document.getElementById('betconfirm') != null
        ) {
            matchStatus = 'betting'
            betConfirmed = document.getElementById('betconfirm') != null
        } else {
            matchStatus = 'ongoing'
        }
    }

    let status = {
        matchStatus: matchStatus,
        betConfirmed: betConfirmed,
        loggedIn: loggedIn,
    }

    chrome.storage.local.set({ status: status }, () => {})

    if (LAST_STATUS != status) {
        LAST_STATUS = status
        FETCHED_FIGHTER_DATA = false
    }

    return status
}

function getFighterData(status) {
    if (
        status['matchStatus'] != 'betting' ||
        status['betConfirmed'] == true ||
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
        fighterRedBtn.value != matchData['fighter_red'] ||
        fighterBlueBtn.value != matchData['fighter_blue']
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
    if (matchData['match_format'] == 'tournament') {
        // Always bet max in tourneys
        betData['confidence'] = 1
    }

    let balance = parseInt(
        document.getElementById('balance').innerText.replace(',', '')
    )
    wagerInput.value = Math.round(
        getWagerAmount(balance, betData['confidence'])
    ).toString()
    if (betData['colour'] == 'red') {
        fighterRedBtn.click()
    } else {
        fighterBlueBtn.click()
    }
}

function getWagerAmount(balance, confidence) {
    return balance * confidence * MAX_BET_PERCENTAGE
}

setInterval(run, RUN_INTERVAL)
