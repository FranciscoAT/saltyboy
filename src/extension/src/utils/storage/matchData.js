/**
 *
 * @param {object} betData - Bet Data, object of form:
 *  ```
 *  {
 *      "confidence": [0, 1],
 *      "inFavourOf": "blue" | "red"
 *  }
 *  ```
 * @param {object} matchData - Match Data, object of form: https://salty-boy.com/apidocs/#/default/get_current_match
 * @returns
 */
function setCurrentMatchData(betData, matchData) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                currentData: {
                    confidence: betData.confidence,
                    inFavourOf: betData.colour,
                    matches: matchData.fighter_red_info?.matches,
                    mode: matchData.match_format,
                    tier: matchData.tier,
                    red: {
                        name: matchData.fighter_red,
                        id: matchData.fighter_red_info?.id,
                        totalMatches:
                            matchData.fighter_red_info?.stats?.total_matches,
                        winRate: matchData.fighter_red_info?.stats?.win_rate,
                        elo: matchData.fighter_red_info?.elo,
                        tierElo: matchData.fighter_red_info?.tier_elo,
                    },
                    blue: {
                        name: matchData.fighter_blue,
                        id: matchData.fighter_blue_info?.id,
                        totalMatches:
                            matchData.fighter_blue_info?.stats?.total_matches,
                        winRate: matchData.fighter_blue_info?.stats?.win_rate,
                        elo: matchData.fighter_blue_info?.elo,
                        tierElo: matchData.fighter_blue_info?.tier_elo,
                    },
                },
            },
            () => {
                res()
            }
        )
    })
}

/**
 *
 * @returns {object} - Of form, see `setCurrentMatchData`.
 */
function getCurrentMatchData() {
    return new Promise((res) => {
        chrome.storage.local.get(['currentData'], (result) => {
            res(result.currentData)
        })
    })
}

/**
 * Initializes current match data
 */
function initializeCurrentMatchData() {
    return setCurrentMatchData({}, {})
}

export { initializeCurrentMatchData, setCurrentMatchData, getCurrentMatchData }
