/**
 * Set the current app settings.
 *
 * @param {boolean} enableOverlay - Enable or disable injection of custom HTML elements for current fighter details.
 * @returns
 */
function setAppSettings(enableOverlay) {
    return new Promise((res) => {
        chrome.storage.local.set(
            {
                appSettings: {
                    enableOverlay: enableOverlay,
                },
            },
            () => {
                res()
            }
        )
    })
}

/**
 * Get app settings.
 *
 * @returns {object} - Returns an object of the form:
 *  ```
 *  {
 *      "enableOverlay": boolean,
 *  }
 *  ```
 */
function getAppSettings() {
    return new Promise((res) => {
        chrome.storage.local.get(['appSettings'], (result) => {
            res(result.appSettings)
        })
    })
}

/**
 * Initializes storage of app settings if not already set
 *
 * @param {boolean} enableOverlay - Enable or disable injection of custom HTML elements for current fighter details.
 * @returns
 */
function initializeAppSettings(enableOverlay) {
    return getAppSettings().then((appSettings) => {
        if (appSettings != null || appSettings != null) {
            function getDefault(defaultValue, key) {
                if (!appSettings.hasOwnProperty(key)) {
                    return defaultValue
                }

                let storedValue = appSettings.key

                if (storedValue == null || storedValue == undefined) {
                    return defaultValue
                }

                return storedValue
            }

            enableOverlay = getDefault(enableOverlay, 'enableOverlay')
        }

        return setBetSettings(enableOverlay)
    })
}

export { initializeAppSettings, getAppSettings, setAppSettings }
