/**
 * Set debug information for background scripts
 *
 * @param {boolean} debugEnabled
 * @returns
 */
function setDebugSettings(debugEnabled) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                debugSettings: {
                    debugEnabled: debugEnabled,
                },
            },
            () => {
                res()
            }
        )
    })
}

/**
 * Get the current debug settings
 *
 * @returns {object} - Should be an object of the following form:
 *  ```
 *  {
 *      "debugEnabled": boolean
 *  }
 */
function getDebugSettings() {
    return new Promise((res) => {
        chrome.storage.local.get(['debugSettings'], (result) => {
            res(result.debugSettings)
        })
    })
}

/**
 * Initializes the match status
 */
function initializeDebugSettings() {
    return getDebugSettings().then((debugSettings) => {
        if (debugSettings == null || debugSettings == undefined) {
            setDebugSettings(false)
            return
        }

        if (!debugSettings.hasOwnProperty('debugEnabled')) {
            setDebugSettings(false)
            return
        }
    })
}

export { getDebugSettings, setDebugSettings, initializeDebugSettings }
