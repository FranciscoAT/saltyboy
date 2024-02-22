## Project Structure

This project has three specific components. A Bot, Web service, and Chrome Extension.

The source code for each can be found at the following locations:
- Bot: [`applications/bot/`](../applications/bot/)
- Web service: [`applications/web/`](../applications/web/)
- Chrome Extension: [`applications/extension/`](../applications/extension/)

### Bot

The goal of the Bot is to connect to the Twitch SaltyBet IRC channel. Then read from the
`waifu4u` bot user messages to determine the current state of SaltyBet and 
record the information into a local database. 

The solution is written in Python and uses Python sockets to interface with the Twitch
IRC chat, dumps the data into a PostgreSQL database.

### Web service

The Web service provides a way for users, including the Chrome Extension, to interface
with the content in the database. The Web service is a light weight service providing
a rather verbose API using Flask and Pydantic, written in Python.

The Web service is also able to provide information about the current state of SaltyBet
by reading from a special table in the PostgreSQL database called `current_match` which
only ever holds a single row detailing the information of the current match. The Web
service can then cross reference this information with the data stored in other places 
in the database namely the `fighter` and `match` tables.

### Chrome Extension

The Chrome Extension provides the ability to allow for the user to let it bet for them
during SaltyBet matches. The Chrome Extension, written in Javascript, provides a myriad
of configuration options including but not limited to:
- Betting strategy.
- Betting limits.
- Different tournament or exhibition mode behaviours.
- Modifying the UI to display relevant information from SaltyBoy.
- And more...