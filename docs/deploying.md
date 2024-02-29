## Deploying

To deploy the service you can leverage using the 
[`docker-compose.yml`](../docker-compose.yml) file. Be sure that you've filled out the 
`.env` file correctly. In particular setting:

- Setting the `GID` / `UID`:
    - `UID=` to your user id. Can be got running `id`.
    - `GID=` to your group id. Can be got running `id`.
    - Note: That these need to be the deploying users!
- `POSTGRES_PORT_EXTERNAL=` set to a Port that want to expose PostgreSQL to.
- Log paths:
    - `BOT_LOG_PATH=` path to where you want logs to be stored for bot.
    - `WEB_LOG_PATH=` path to where you want logs to be stored for web server.
    - These are the paths on your local machine. Need to ensure that the running user
        has r/w ability for the directory and that the directory exists.
- `DEBUG=` optionally set it to `DEBUG=1` to have the system output debug logs.
- `POSTGRES_HOST=postgres` **important!**. This is inside of a Docker network and we
    will access it using the name of the Postgres Docker compose service name.
- `POSTGRES_PORT=5432`. Since we are using `POSTGRES_HOST=postgres` we need to reach
    into Postgres on the port it is listening to inside of the Docket network.
- `POSTGRES_USER=` / `POSTGRES_PASSWORD=` / `POSTGRES_DB=` can be set to whatever you
    like. Please do update `POSTGRES_PASSWORD=`!
- `TWITCH_USERNAME=`, and `TWITCH_OAUTH_TOKEN=` should be set accordingly. See
    [Setup](./setup.md#twitch-irc-token).

Then you can build and run the services:

```sh
docker-compose build
docker-compose up -d
```

### Expose it Externally

If you want to expose the service to the external world. I would recommend you set up 
an [Nginx](https://nginx.org/en/), or other HTTP reverse proxy server. Ensure that 
you've also setup SSL using a service such as [Let's Encrypt](https://letsencrypt.org/).

Note if using Nginx you'll need to ensure in order for the Chrome Extension to be able
to reach your side you'll need to enable CORS as necessary. To do so you can use an
Nginx block like so:

```
location / {
        add_header "Access-Control-Allow-Origin" https://www.saltybet.com;
        ...
        proxy_pass ...;
}
```

### Deploying the Extension

Naturally, this won't deploy the extension. To deploy the extension please see 
[Developing](./developing.md#building-the-extension), and then go through the process
of getting the Chrome Extension approved on the 
[Chrome Web Store](https://chromewebstore.google.com/).

Note, that should you want to use your deployed web service with your version of the
Chrome Extension you'll need to update the `SALTYBOY_URL` variable in the extension.
Please read [Developing](./developing.md#chrome-extension) for more information.