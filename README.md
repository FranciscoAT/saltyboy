# Salty Boy

Simple betting tool bot for usage in [Salty Bet](https://saltybet.com).

The project is split up into three parts:

- [Bot](#bot) which is the software that will catalog fighters and matches.
- [Web](#web) service interface interacts with the database and provides ability to view content of current match along with fighter details.
- [Extension](#extension) Chrome extension to be used on the Saltybet website that interfaces with the web service and bets for you according to the currently selected betting mode along with providing many different configurations for betting.

The project is currently running and live. You can view more on https://salty-boy.com. You can alternatively use the already working [Chrome Extension](https://chrome.google.com/webstore/detail/salty-boy/khlbmnneeaecmpeicbaodeaeicljnddj) which is hooked up by default to https://salty-boy.com and have it start betting for you right away!


## Bot

Code found in `bot` is used for cataloging all the matches, and every fighter. The longer this runs the better data the tool will have to bet.

The bot will track all Tournament and Matchmaking matches and fighters. Exhibition matches are ignored.

### Running

1. Under `db` create a new file called whatever you want. This will serve as the SQLLite3 DB file.
1. Create a new `.env` file under `bot`, fill it with the following:
    - `USERNAME=<username>`, replace `<username>` with your Twitch account username.
    - `OAUTH_TOKEN=<oauth_token>`, replace `<oauth_token>` with your Twitch account OAuth Token.
        - You can quickly get it from here https://twitchapps.com/tmi/. It should be of the format `"oauth:<str>"`.
    - `DATABASE_PATH=<db_path>`, replace `<db_path>` with the path to the database file.
    - `DATABASE_URI=<db_uri>`, replace `<db_uri>` with same contents as `<db_path>` but prepend `sqlite:///`.


Now we are ready to start the service.

- Start up the service as Docker container:
    ```
    $ docker-compose up --build -d bot
    ```
- Start up the service manually:
    ```
    $ cd bot
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    (.venv) $ pip install -r requirements.txt
    (.venv) $ alembic upgrade head
    (.venv) $ python main.py
    ```
    - Flags:
        - `-d`/`--debug` flag to include DEBUG logs
        - `-lp <path>`/`--log-path <path>` to also log information to disk

The bot will now begin tracking and cataloging fighters and matches.

## Web

Code found in the `web` is used for interfacing with the data stored in the SQLLite3 database.

If you want to find the a live version of this service you can find it here along with some more information: https://salty-boy.com.

### Running

1. Ensure you've done everything under [running the bot](#bot-running)
1. Create a new `.env` file under `bot`, fill it with the following:
    - `DATABASE_PATH=<db_path>`, this should be the same as the environment variable defined in the `bot` section
    - `DEPLOYMENT_MODE=PROD`, if set to this it will deploy using HTTPS and UWSGI otherwise set it to whatever you want and it will run as a development server
    - `SWAGGER_SERVER=<url>` optional, value defaults to `http://localhost:5000`, but if you are deploying it somewhere update this value so that the Swagger docs uses the given URL

We are ready to spin up the service:

- Start up the service as a Docker container:
    ```
    $ docker-compose up --build -d web
    ```
- Start up the service manually:
    ```
    $ cd web
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    (.venv) $ pip install -r requirements.txt
    (.venv) $ python main.py
    ```
    - Flags:
        - `-d`/`--debug` flag to include DEBUG logs
        - `-lp <path>`/`--log-path <path>` to also log information to disk


## Extension

The Extension is available in the [Chrome Web Store](https://chrome.google.com/webstore/detail/salty-boy/khlbmnneeaecmpeicbaodeaeicljnddj). Otherwise you can follow the next steps to set up an editable version of the Chrome Extension.

### Setting up the Extension

1. Install `npm` & `node`
    - Consider looking into `nvm` for installing `node`
1. Navigate to the `extension` folder
1. Run `npm install`
1. Run `npm run build`
1. A `dist` folder should now be created
1. Navigate to `chrome://extensions` in Google Chrome
1. Click on "Load Unpacked"
1. Find the `dist` directory on your computer and select it

The Chrome Extension is now installed and working. Simply navigate to https://saltybet.com and login and it will begin betting for you.

If you want to update the Bot. Just update the code on disk and click the "Update" button on the `chrome://extensions` page. Reminder you'll also have to reload the SaltyBet webpage if you had it open when updating the extension.

Should you want to make your own changes to the project. Simply edit the files in `extension/src` and re-run `npm run build`, you can also run `npm run dev` which will automatically update the `dist` directory are you update the files. Depending on your changes you may also need to update `manifest.json` and or `webpack.config.js`.

### Building the extension on Windows

1. Open `package.json` in the `extension` folder in a text editor such as Notepad++
2. Change the lines in "build" to this with copy and paste `"build": "npx webpack --config webpack.config.js && 7z a saltyboy.zip dist/",`
3. You will need to install [7zip](https://www.7-zip.org/download.html) Install into the default location. After this we need to set the environmental variables.
4. Windows Key + R on your keyboard and type "cmd"
5. In the command prompt window you need to copy and paste. `'set PATH=%PATH%;C:\Program Files\7-Zip\
echo %PATH% 
7z' ` Modify the path accordingly if you installed it elsewhere.
6. Now that you've done this you should be able to Run in a command prompt `npm run build` if not, restart your PC and verify the path is set in Windows correctly for 7zip in the environmental variables.


### Creating a new Betting Method

You can create a new betting method by creating a new file in `extension/src/content_scripts/bet_modes`. Create a function in that file that takes in the `matchDat` object. Then return an object of the following format:

```json
{
    "confidence": <value between 0 to 1>,
    "colour": <"red"|"blue">
}
```

After you can then import the function in `extension/src/content_scripts/main.js` and add it to the `BET_MODES` constant. From there update `extension/src/popup/popup.js` `BET_MODE_INFO` constant accordingly. Finally, add the new bet mode as an option inside of the dropdown in `extension/src/popup/popup.html`.

----

## Acknowledgements

- All the FOSS chads who provide their 3rd party libraries to make this project possible
- [Salty Bet](https://saltybet.com) into the salt mines!! 
- [favicon.ico](web/public/favicon.ico) was made by [Freepik](https://www.freepik.com) and can be found on [Flaticon](https://www.flaticon.com)
