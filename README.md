# Saltyboy

Simple betting tool bot for usage in [Saltybet](https://saltybet.com).

The project is split up into three parts:

- [Bot](#bot) which is the software that will catalog fighters and matches.
- [Web](#web) web service interface that will determine the best outcome for two given fighters.
- [Extension](#extension) Chrome extension to be used on the Saltybet website that interfaces with the Web service


## Bot

Code found in `bot` is used for cataloging all the matches, and every fighter. The longer this runs the better data the tool will have to bet.

The bot will track all Tournament and Matchmaking matches and fighters. Exhibitions are currently ignored.

### Running

1. Under `db` create a new file called whatever you want. This will serve as the SQLLite3 DB file.
1. Create a new `.env` file under `bot`, fill it with the following:
    - `USERNAME=<username>`, replace `<username>` with your Twitch account username.
    - `OAUTH_TOKEN=<oauth_token>`, replace `<oauth_token>` with your Twitch account OAuth Token.
        - You can quickly get it from here https://twitchapps.com/tmi/. It should be of the format `"oauth:<some characters>"`.
    - `DATABASE_PATH=<db_path>`, replace `<db_path>` with the relative path to the database. Generally this should be `../db/<db_name>` where `<db_name>` is what you named your SQLLite3 DB file in step 1.
    - `DATABASE_URI=<db_uri>`, replace `<db_uri>` with same contents as `<db_path>` but prepend `sqlite:///` in-front of the relative path. Optionally you can use `sqlite:////` and specify an absolute path.


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
    (.venv) $ python main.py
    ```
    - Flags:
        - `-d`/`--debug` flag to include DEBUG logs
        - `-lp <path>`/`--log-path <path>` to also log information to disk

The bot will now begin tracking and cataloging fighters and matches.

## Web

Code found in the `web` is used for interfacing with the data stored in the SQLLite3 database.

### Running

1. Ensure you've done everything under [running the bot](#bot-running)
1. Create a new `.env` file under `bot`, fill it with the following:
    - `DATABASE_PATH=<db_path>`, this should be the same as the environment variabled defined in the `bot` section

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
        - `-p`/`--prod` flag to set the app to run in production mode. This will cause it to run on `0.0.0.0` instead of `localhost` and turn off Flasks `debug` mode
        - `-lp <path>`/`--log-path <path>` to also log information to disk


### Querying the Webapp

NB: Unfortunately the DB is case sensitive. A TODO for down the road

#### Get Fighter Information

Endpoint: `GET /fighters`

Query Parameters:
    - Expects one of:
        - `id=<int>` where `<int>` is the database id of the fighter
        - `name=<str>` where `<str>` is the name of the fighter

Returns:
    - 200:
        ```
        {
            "fighter": {
                "id": <int>,
                "name": <str>,
                "best_streak": <int>,
                "tier": <str>,
                "last_updated": <datetime>,
                "creation_time": <datetime>,
            },
            "stats": {
                "average_bet": <float>,
                "win_rate": <float>,
                "total_matches": <int>
            }
        }
        ```
    - 400: Bad Request
    - 404: Fighter not found


#### Analyze Match Between Fighters


Endpoint: `POST /analyze`

JSON Payload:
    ```
    {
        "fighter_red": {
            "name": <str>,
            "id": <int>
        },
        "fighter_blue": {
            "name": <str>,
            "id": <int>
    }
    ```
    - Each expects one of a `name` or `id`

Returns:
    - 200:
        ```
        {
            "red": {
                "fighter": {
                    "id": <int>,
                    "name": <str>,
                    "best_streak": <int>,
                    "tier": <str>,
                    "last_updated": <datetime>,
                    "creation_time": <datetime>,
                },
                "stats": {
                    "average_bet": <float>,
                    "win_rate": <float>,
                    "total_matches": <int>
                },
                "stats_vs": {
                    "average_bet_vs": <float>,
                    "win_rate_vs": <float>,
                    "total_matches_vs": <int>
                }
            },
            "blue": {
                // Same contents as "red" but for "fighter_blue"
            },
            "suggested_bet": <"red" or "blue">,
            "confidence": <float between 0.0 to 1.0>
        }
        ```
    - 400: Bad Request
    - 404: One of the fighters was not found
