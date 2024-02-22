## Setup

1. Install the following:
    - Install [Docker](https://www.docker.com/).
    - Install [Docker Compose](https://docs.docker.com/compose/).
    - Install [Python](https://www.python.org/).
    - Install [Python Poetry](https://python-poetry.org/).
    - Install [GNU Make](https://www.gnu.org/software/make/).
    - Install [Node Version Manager](https://github.com/nvm-sh/nvm)
        - Optionally, you can install Node and NPM individually.
        - If using `nvm` run `nvm install node && nvm use node` to install and use the
            latest Node and NPM versions.
1. Copy the contents of [`.template.env`](../.template.env) to a `.env` file and update 
    the contents accordingly.
1. Install the dependencies using `make install`.
1. You can now run the applications:
    - For local development:
        - `make run-bot` --> Run the Bot.
        - `make run-web` --> Run the Web service.
    - As a Docker instance:
        - `make docker-up` --> Runs Bot & Web service.
        - Note: You may also want to use `docker-build` to rebuild the containers 
            provided any code changes exist.

### Twitch IRC

In order for the Bot to connect ot the Twitch IRC you'll want to create a Twitch OAuth
token. Go to https://twitchapp.com/tmi/ to generate your token. Ensure that the value
you put for `OAUTH_TOKEN` in your `.env` file is of the form `oauth:<your_token_here>`.