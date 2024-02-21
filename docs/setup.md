## Setup

1. Install the following:
    - Install [Docker](https://www.docker.com/).
    - Install [Docker Compose](https://docs.docker.com/compose/).
    - Install [Python](https://www.python.org/).
    - Install [Python Poetry](https://python-poetry.org/).
    - Install [GNU Make](https://www.gnu.org/software/make/).
1. Copy the contents of [`.template.env`](../.template.env) to a `.env` file and update 
    the contents accordingly.
1. You can now run the applications:
    - For local development:
        - `make run-bot` --> Run the Bot.
        - `make run-web` --> Run the Web service.
    - As a Docker instance:
        - `make docker-up` --> Runs Bot & Web service.
        - `make docker-up-bot` --> Runs Bot.
        - `make docker-up-web` --> Runs Web service.
        - Note: You may also want to use `docker-build` and `docker-build-<x>` to 
            rebuild the containers provided any code changes exist.