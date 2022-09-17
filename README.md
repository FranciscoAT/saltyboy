# Salty Boy

Simple betting tool bot for usage in [Salty Bet](https://saltybet.com).

The project is split up into three parts:

- [Bot](#bot) which is the software that will catalog fighters and matches.
- [Web](#web) service interface interacts with the database and provides ability to view content of current match along with fighter details.
- [Extension](#extension) Chrome extension to be used on the Saltybet website that interfaces with the web service and bets for you according to the currently selected betting mode along with providing many different configurations for betting.

The project is currently running and live. You can view more on https://salty-boy.com. You can alternatively use the already working [Chrome Extension](https://chrome.google.com/webstore/detail/salty-boy/khlbmnneeaecmpeicbaodeaeicljnddj) which is hooked up by default to https://salty-boy.com and have it start betting for you right away!

## Bot

Code found in [`bot`](bot/) is used for cataloging all the matches, and every fighter. The longer this runs the better data the tool will have to bet.

The bot will track all Tournament and Matchmaking matches and fighters. Exhibition matches are ignored.

### Running the Bot

1. If you wish to run manually:
    1. Install Python 3.10.x.
    1. Install [Python Poetry 1.2.x](https://python-poetry.org/docs/).
1. If you wish to run via Docker:
    1. Install [Docker](https://docs.docker.com/engine/install/)
    1. (Optional) Install [Docker Compose](https://docs.docker.com/compose/install/)
1. Under [`db`](db/) create a new file called whatever you want. This will serve as the SQLLite3 DB file.
    - I do have considerations changing this to a PostgreSQL database in the future.
1. Create a new `.env` file under `bot`, fill it with the following:
    - `USERNAME=<username>`, replace `<username>` with your Twitch account username.
    - `OAUTH_TOKEN=<oauth_token>`, replace `<oauth_token>` with your Twitch account OAuth Token.
        - You can quickly get it from here https://twitchapps.com/tmi/. It should be of the format `"oauth:<str>"`.
    - `DATABASE_PATH=<db_path>`, replace `<db_path>` with the path to the database file.
    - `DATABASE_URI=<db_uri>`, replace `<db_uri>` with same contents as `<db_path>` but prepend `sqlite:///`.

Now we are ready to start the service.

- Start up the service as Docker container:
    ```sh
    docker-compose up --build -d bot
    ```
    You can optionally manually build the container from the [Dockerfile](bot/Dockerfile), just be aware to mount the [`logs`](logs/) directory to the Containers `/opt/logs`.
- Start up the service manually:
    ```sh
    poetry install
    poetry run alembic upgrade head
    poetry run python main.py
    ```
    You can run `poetry run python main.py --help` to view information about any flags you can pass into the service.

The bot will now begin tracking and cataloging fighters and matches.

## Web

Code found in the [`web`](web/) is used for interfacing with the data stored in the SQLLite3 database.

If you want to find the a live version of this service you can find it here along with some more information: https://salty-boy.com.

### Running the Web Server

1. If you wish to run manually:
    1. Install Python 3.10.x.
    1. Install [Python Poetry 1.2.x](https://python-poetry.org/docs/).
1. If you wish to run via Docker:
    1. Install [Docker](https://docs.docker.com/engine/install/)
    1. (Optional) Install [Docker Compose](https://docs.docker.com/compose/install/)
1. Ensure you've done everything under [Running the Bot](#running-the-bot) section.
1. Create a new `.env` file under `bot`, fill it with the following:
    - `DATABASE_PATH=<db_path>`, this should be the same as the environment variable defined in the `bot` section
    - `DEPLOYMENT_MODE=PROD`, if set to this it will deploy using HTTPS and UWSGI otherwise set it to whatever you want and it will run as a development server
    - `SWAGGER_SERVER=<url>` optional, value defaults to `http://localhost:5000`, but if you are deploying it somewhere update this value so that the Swagger docs uses the given URL

We are ready to spin up the service:

- Start up the service as a Docker container:
    ```sh
    docker-compose up --build -d web
    ```
    You can optionally manually build the container from the [Dockerfile](web/Dockerfile), just be aware to mount the [`logs`](logs/) directory to the Containers `/opt/logs`.
- Start up the service manually:
    ```sh
    cd web && poetry install
    poetry run python main.py
    ```
    You can run `poetry run python main.py --help` to view information about any flags you can pass into the service.

## Extension

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
