## Developing

### Bot

To develop the Bot. Ensure you have your `.env` file properly setup. Then you can run
`make bot-run` from the project root to run the Bot. Unfortunately, this does not 
support auto-restarts on code changes. You'll have to re-run this command on each code
change.

It can be hard to develop with the bot as it actively reads form the SaltyBet chat. It 
is recommended to have the bot run once you feel it is ready locally for at least the 
entire length of a SaltyBet modes. ie. Let it run a full cycle through Matchmaking, 
Tournament, and Exhibition. To ensure the bot works as expected.

**Note**: Twitch does not like two of the same user to be logged into a single
chat room multiple times at the same time. Therefore if you have SaltyBet open in a 
different window it is **highly** advisable that you run SaltyBet in a session where
you are not logged into Twitch currently to avoid any weird interactions and the bot
randomly crashing.

### Web service

The Web service is a simple Flask application. To develop with it however, you'll need
a PostgreSQL database dump. To get one please just ping me and I'll generate you a dump
at my earliest convenience. Then leverage `psql` command to load up your database. 
Alternatively, run a local [Bot](#bot) instance to start filling up the database with
live data for you.

### Chrome Extension

To develop with Chrome Extension. You'll want to modify the necessary source code under
[`src/extension/src/`](../src/extension/src/). You can then run `make run-extension` 
which will just call `npm run dev` under the hood. This will take any code under the 
Extension's source directory and compile it into individual files under 
[`src/extension/dist/`](../src/extension/dist/). Very important to note to not edit
any of these files! From here you can then run the Extension from these local files:
1. Navigate to `chrome://extensions` in Chrome.
1. Ensure you have "Developer Mode" enabled in the top right of this page.
1. Click on "Load Unpacked".
1. Find the `dist` directory in the file explorer and select it.

The Extension should now be working when you go to https://saltybet.com. When you update
the extension click on the "Update" button under the card for your local extension in 
`chrome://extensions`. Note that you may also need to refresh the SaltyBet web page.

The extension is hard-coded to reach out to https://salty-boy.com. However, should you
want to use a local instance you'll need to edit the `SALTY_BOY_URL` accordingly in 
[`main.js`](../src/extension/src/content_scripts/main.js).

If you have a local extension running to disable the live 
SaltyBoy extension, if installed, to avoid them from colliding with each other. 

Note that depending on your changes you may also need to update either: 
[`manifest.json`](../src/extension/src/manifest.json), and or 
[`webpack.config.js`](../src/extension/webpack.config.js) depending on any file 
structure changes to ensure your files are getting built and thrown in 
[`dist/`](../src/extension/dist/).

### New Bet Method

If your goal is just create a new betting method please read the above then do the 
following:

1. You can create a new betting method by creating a new file  under the
    [`bet_modes/`](../src/extension/src/content_scripts/bet_modes/) directory. Create a
    function in that file that takes in the `matchData` object and returns an object of 
    the following format:
    ```json
    {
        "confidence": <value between 0 to 1>,
        "colour": <"red"|"blue">
    }
    ```
1. Import the function in [`main.js`](../src/extension/src/content_scripts/main.js) and 
    add it to the `BET_MODES` constant variable. 
1. Update [`popup.js`](../src/extension/src/popup/popup.js) `BET_MODE_INFO` constant
    variable accordingly. 
1. Add the new bet mode as an option inside of the dropdown in 
    [`popup.html`](../src/extension/src/popup/popup.html).

#### Building the Extension

To build the extension formally into a `.zip` that can be submitted to the Chrome 
Extensions Web Store, do the following:

1. Update the version [`manifest.json`](../src/extension/src/manifest.json) accordingly.
1. Build the extension:
    - On Linux (WSL):
        1. Run `make build-extension`
    - On Windows:
        1. Install 7-Zip and make sure it is in your Windows Path:
            1. Install [7-Zip](https://7-zip.org/).
            1. Open up a Command Prompt or Powershell window:
                1. Win Key + R.
                1. Type `cmd` then hit Enter.
            1. Update your `PATH` variable:
                ```sh
                set PATH=%PATH%;C:\Program Files\7-Zip\
                ```
                - You can confirm your path by running `7z --help`.
                - You may need to update the above command if you installed 7-Zip 
                    elsewhere on your system.
            1. From the extension root under [`src/extension`](../src/extension/) run
                `npm run build-win`.
1. A file name `saltyboy.zip` should be generated under 
    [`src/extension`](../src/extension/). This is the final packed extension.
