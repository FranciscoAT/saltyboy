// --- MATCH STATUS ---
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

// --- BET SETTINGS ---
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

// --- CURRENT BET DATA ---
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
                    inFavourOf: inFavourOf,
                },
            },
            () => {
                res()
            }
        )
    })
}

// --- WINNINGS ---
function getStorageWinnings() {
    return new Promise((res) => {
        chrome.storage.local.get(['winnings'], (result) => {
            res(result.winnings)
        })
    })
}

function updateStorageWinnings(winningIncrease) {
    return new Promise((res) => {
        getStorageWinnings().then((winnings) => {
            let newWinnings = {
                total: winningIncrease,
                session: winningIncrease,
            }

            if (winnings != null) {
                if (winnings.total != null) {
                    newWinnings.total += winnings.total
                }
                if (winnings.session != null) {
                    newWinnings.session += winnings.session
                }
            }

            chrome.storage.local.set(
                {
                    winnings: newWinnings,
                },
                () => {
                    res()
                }
            )
        })
    })
}

function resetStorageSessionWinnings() {
    return new Promise((res) => {
        getStorageWinnings(res).then((winnings) => {
            let newWinnings = {
                total: 0,
                session: 0,
            }

            if (winnings != null && winnings.total != null) {
                newWinnings.total = winnings.total
            }

            chrome.storage.local.set(
                {
                    winnings: newWinnings,
                },
                () => {
                    res()
                }
            )
        })
    })
}

export {
    setStorageMatchStatus,
    getStorageMatchStatus,
    setStorageBetSettings,
    getStorageBetSettings,
    setStorageCurrentBetData,
    getStorageCurrentBetData,
    getStorageWinnings,
    updateStorageWinnings,
    resetStorageSessionWinnings
}
