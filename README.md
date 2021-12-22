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
    - `DEPLOYMENT_MODE=PROD`, if set to this it will deploy using HTTPS and UWSGI

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


### Querying the Webapp

__NB__: Unfortunately the DB is case sensitive. A TODO for down the road

#### Querying DB Stats

Returns some total stats about the number of matches and fighter cataloged. Along with a break down total based on the tiers.

__Endpoint__: `GET /stats`

__Returns__:

- 200:
    ```
    {
        "fighters": {
            "break_down": [
                {
                    "tier": <string>, 
                    "fighter_count": <int>
                }
            ],
            "total": <int>
        },
        "matches": {
            "break_down": [
                {
                    "tier": <string>,
                    "match_count": <int>
                }
            ],
            "total": <int>
        }
    }
    ```


#### Get Fighter Information

Returns information specific to a given fighter. Includes all the fighters associated matches, their current rank, best win streak, along with some averaged stats.

__Endpoint__: `GET /fighters`

__Query Parameters__:

Expects one of:

- `id=<int>` where `<int>` is the database id of the fighter
- `name=<str>` where `<str>` is the name of the fighter

__Returns__:

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
        },
        "matches": [
            {
                "bet_blue": <int>,
                "bet_red": <int>,
                "colour": <string>, // winning colour
                "date": <datetime>,
                "fighter_blue": <int>,
                "fighter_red": <int>,
                "id": <int>,
                "match_format": <"tournament" or "matchmaking">,
                "streak_blue": <int>,
                "streak_red": <int>,
                "tier": <string>,
                "winner": <int>
            }
        ]
    }
    ```
- 400: Bad Request
- 404: Fighter not found


#### Analyze Match Between Fighters

__NB__: The logic on the `confidence` is extremely naive at the moment, and I have considerations of moving the computation to the extension to off-load resource intensive operations to the client. tl;dr considering dropping this endpoint.

Analyzes the winning probability between two given fighters, and includes some stats about the fighters and the matches they've had between each other.

__Endpoint__: `POST /analyze`

__JSON Payload__:

```
{
    // Each expect one of `name` or `id` and not both
    "fighter_red": {
        "name": <str>,
        "id": <int>
    },
    "fighter_blue": {
        "name": <str>,
        "id": <int>
}
```

__Returns__:

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


## Extension

TBD

----

## Acknowledgements

- [Saltybet](https://saltybet.com) for their awesome service they provide!
- [Twitch](https://twitch.com) for their great IRC chatrooms!
- [favicon.ico](web/public/favicon.ico) was made by [Freepik](https://www.freepik.com) and can be found on [Flaticon](https://www.flaticon.com)
