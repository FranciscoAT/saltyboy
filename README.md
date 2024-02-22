# Salty Boy

Simple betting tool and betting bot bot for usage in [Salty Bet](https://saltybet.com). 
SaltyBoy is currently hosted at https://salty-boy.com. With a live 
[Chrome Extension](https://chrome.google.com/webstore/detail/salty-boy/khlbmnneeaecmpeicbaodeaeicljnddj)
that you can use right now!

## Developing

For more information on how to develop or run SaltyBoy see [Setup](./docs/setup.md)
and [Project Structure](./docs/project_structure.md).


The Extension is available in the [Chrome Web Store](https://chrome.google.com/webstore/detail/salty-boy/khlbmnneeaecmpeicbaodeaeicljnddj). Otherwise you can follow the next steps to set up an editable version of the Chrome Extension.

### Running the Extension

1. Install [`npm`](https://www.npmjs.com/) & [`node`](https://nodejs.org/en/).
    - Consider looking into [`nvm`](https://github.com/nvm-sh/nvm) for installing [`node`](https://nodejs.org/en/).
1. Run the following:
    ```sh
    npm install
    npm run build
    ```
1. A `dist` folder should now be created under `extension/`.
1. Navigate to `chrome://extensions` in Google Chrome.
1. Click on "Load Unpacked".
1. Find the `dist` directory on your computer and select it.
    - Path should be `<path to project>/extension/dist/`

The Chrome Extension is now installed and working. Simply navigate to https://saltybet.com and login and it will begin betting for you.

If you want to update the Bot. Just update the code on disk and click the "Update" button on the `chrome://extensions` page. Reminder you'll also have to reload the SaltyBet webpage if you had it open when updating the extension.

Should you want to make your own changes to the project. Simply edit the files in [`extension/src/`](extension/src/) and re-run `npm run build`, you can also run `npm run dev` which will automatically update the `dist/` directory when you alter any files under the `src/` directory. Depending on your changes you may also need to update [`manifest.json`](extension/src/manifest.json) and or [`webpack.config.js`](extension/webpack.config.js).

### Building the Extension

#### Linux

1. Ensure you have `zip` installed.
1. Run `npm run build`. 
1. A file named `saltyboy.zip` should be generated under [`extension/`](extension/).

#### Windows

1. Install [7-Zip](https://www.7-zip.org/download.html)
1. Add 7-Zip to your Windows Path:
    1. Hit: Windows Key + R on your keyboard and type `cmd`
    1. In the command prompt window enter the following:
        ```sh
        set PATH=%PATH%;C:\Program Files\7-Zip\
        echo %PATH%
        ```
        - **Note** as always be careful when altering you `PATH` variable. Please read up on the topic if you are not certain what the above does!
        -  You may need to alter the `PATH` string in the event you installed 7-Zip elsewhere.
1. Run `npm run build-win`
1. A file named `saltyboy.zip` should be generated under [`extension/`](extension/).

### Creating a new Betting Method

1. You can create a new betting method by creating a new file  under [`extension/src/content_scripts/bet_modes/`](extension/src/content_scripts/bet_modes/). Create a function in that file that takes in the `matchData` object and returns an object of the following format:
    ```json
    {
        "confidence": <value between 0 to 1>,
        "colour": <"red"|"blue">
    }
    ```
1. Import the function in [`extension/src/content_scripts/main.js`](extension/src/content_scripts/main.js) and add it to the `BET_MODES` constant variable. 
1. Update [`extension/src/popup/popup.js`](extension/src/popup/popup.js) `BET_MODE_INFO` constant variable accordingly. 
1. Add the new bet mode as an option inside of the dropdown in ][`extension/src/popup/popup.html`](extension/src/popup/popup.html).

----

## Acknowledgements

- All the FOSS chads who provide their 3rd party libraries to make this project possible.
- [Salty Bet](https://saltybet.com) into the salt mines!! 
- [favicon.ico](web/public/favicon.ico) was made by [Freepik](https://www.freepik.com) and can be found on [Flaticon](https://www.flaticon.com)
