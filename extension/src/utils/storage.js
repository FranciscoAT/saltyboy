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
function getStorageCurrentData() {
    return new Promise((res) => {
        chrome.storage.local.get(['currentData'], (result) => {
            res(result.currentData)
        })
    })
}

function setStorageCurrentData(betData, matchData) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                currentData: {
                    confidence: betData.confidence,
                    inFavourOf: betData.colour,
                    matches: matchData.fighter_red_info?.matches,
                    red: {
                        id: matchData.fighter_red_info?.id,
                        totalMatches: matchData.fighter_red_info?.stats?.total_matches,
                        winRate: matchData.fighter_red_info?.stats?.win_rate,
                        elo: matchData.fighter_red_info?.elo,
                        tierElo: matchData.fighter_red_info?.tier_elo
                    },
                    blue: {
                        id: matchData.fighter_blue_info?.id,
                        totalMatches: matchData.fighter_blue_info?.stats?.total_matches,
                        winRate: matchData.fighter_blue_info?.stats?.win_rate,
                        elo: matchData.fighter_blue_info?.elo,
                        tierElo: matchData.fighter_blue_info?.tier_elo
                    }
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
    setStorageCurrentData,
    getStorageCurrentData,
    getStorageWinnings,
    updateStorageWinnings,
    resetStorageSessionWinnings
}
