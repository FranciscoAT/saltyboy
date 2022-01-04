function setStorageMatchStatus(currentStatus, betConfirmed, loggedIn) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                matchStatus: {
                    currentStatus: currentStatus,
                    betConfirmed: betConfirmed,
                    loggedIn: loggedIn,
                },
            },
            () => {
                res()
            }
        )
    })
}

function getStorageMatchStatus() {
    return new Promise((res) => {
        chrome.storage.local.get(['matchStatus'], (result) => {
            res(result.matchStatus)
        })
    })
}

function setStorageBetSettings(
    betMode,
    maxBetPercentage,
    maxBetAmount,
    allInTournaments,
    enableBetting,
    dollarExhibitions
) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                betSettings: {
                    betMode: betMode,
                    maxBetPercentage: maxBetPercentage,
                    maxBetAmount: maxBetAmount,
                    allInTournaments: allInTournaments,
                    enableBetting: enableBetting,
                    dollarExhibitions: dollarExhibitions,
                },
            },
            () => {
                res()
            }
        )
    })
}

function getStorageBetSettings() {
    return new Promise((res) => {
        chrome.storage.local.get(['betSettings'], (result) => {
            res(result.betSettings)
        })
    })
}

function getStorageCurrentBetData() {
    return new Promise((res) => {
        chrome.storage.local.get(['currentBetData'], (result) => {
            res(result.currentBetData)
        })
    })
}

function setStorageCurrentBetData(confidence, inFavourOf) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                currentBetData: {
                    confidence: confidence,
                    inFavourOf: inFavourOf
                },
            },
            () => {
                res()
            }
        )
    })
}

export {
    setStorageMatchStatus,
    getStorageMatchStatus,
    setStorageBetSettings,
    getStorageBetSettings,
    setStorageCurrentBetData,
    getStorageCurrentBetData
}
