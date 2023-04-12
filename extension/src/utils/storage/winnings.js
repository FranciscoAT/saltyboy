/**
 *
 * @param {number} winningIncrease - Winning amount, positive or negative
 * @returns
 */
function updateWinnings(winningIncrease) {
    return new Promise((res) => {
        getWinnings().then((winnings) => {
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

/**
 * Get the current winnings.
 *
 * @returns {object} - Object of form:
 *  ```
 *  {
 *      "total": number,
 *      "session": number
 *  }
 *  ```
 */
function getWinnings() {
    return new Promise((res) => {
        chrome.storage.local.get(['winnings'], (result) => {
            res(result.winnings)
        })
    })
}

/**
 * Resets the current session winnings to 0.
 *
 * @returns
 */
function resetSessionWinnings() {
    return new Promise((res) => {
        getWinnings(res).then((winnings) => {
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

export { resetSessionWinnings, updateWinnings, getWinnings }
