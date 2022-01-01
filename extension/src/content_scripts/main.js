const RUN_INTERVAL = 5000
const SALTY_BOY_URL = 'https://www.salty-boy.com'
const MAX_BET_PERCENTAGE = 0.05 // TODO: allow this to be configurable
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
    if (status['matchStatus'] != 'betting' || status['betConfirmed'] == true) {
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

    let balance = parseInt(
        document.getElementById('balance').innerText.replace(',', '')
    )
    let betData = calculateBet(balance, matchData)
    wagerInput.value = Math.round(betData['amount']).toString()
    if (betData['colour'] == 'red') {
        fighterRedBtn.click()
    } else {
        fighterBlueBtn.click()
    }
}

function calculateBet(balance, matchData) {
    /*
     * Calculates the bet. Currently this method is extremely naive and needs improvement.
     *
     * It will always bet $1 red if all else fails on every single match.
     * If it is in tournament mode it will always bet 100% of balance.
     * If the two fighters have fought before it will base calculations on the subset of those
     * matches played together.
     * Otherwise it will base it on their respective win rates.
     */

    let betData = {
        amount: 1,
        colour: 'red',
    }

    if (
        matchData['fighter_red_info'] != null &&
        matchData['fighter_blue_info'] != null
    ) {
        let fighterRedId = matchData['fighter_red_info']['id']
        let fighterBlueId = matchData['fighter_blue_info']['id']

        // First check to see if the two fighters have fought before
        let redWinsVsBlue = 0
        let redMatchesVsBlue = 0
        for (const match of matchData['fighter_red_info']['matches']) {
            if (
                (match['fighter_red'] == fighterRedId &&
                    match['fighter_blue'] == fighterBlueId) ||
                (match['fighter_red'] == fighterBlueId &&
                    match['fighter_blue'] == fighterRedId)
            ) {
                if (match['winner'] == fighterRedId) {
                    redWinsVsBlue += 1
                }
                redMatchesVsBlue += 1
            }
        }

        if (redMatchesVsBlue > 0) {
            let redWinRateVsBlue = redWinsVsBlue / redMatchesVsBlue
            if (redWinRateVsBlue < 0.5) {
                betData['colour'] = 'blue'
                betData['amount'] =
                    (1 - redWinRateVsBlue) * balance * MAX_BET_PERCENTAGE
            } else {
                betData['amount'] =
                    redWinRateVsBlue * balance * MAX_BET_PERCENTAGE
            }
        } else {
            let redWinRate = matchData['fighter_red_info']['stats']['win_rate']
            let blueWinRate =
                matchData['fighter_blue_info']['stats']['win_rate']

            if (redWinRate + blueWinRate == 0) {
                betData['amount'] = 1
            } else if (blueWinRate > redWinRate) {
                betData['colour'] = 'blue'
                betData['amount'] =
                    (blueWinRate / (redWinRate + blueWinRate)) *
                    balance *
                    MAX_BET_PERCENTAGE
            } else {
                betData['amount'] =
                    (redWinRate / (redWinRate + blueWinRate)) *
                    balance *
                    MAX_BET_PERCENTAGE
            }
        }
    }

    if (matchData['match_format'] == 'tournament') {
        // Always bet max on tournament matches
        betData['amount'] = balance
    }

    return betData
}

setInterval(run, 5000)
