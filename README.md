# Salty Boy

This is a program to collect data about [Salty Bet](http://saltybet.com) fights. Then to bet accordingly. Salty Bets is a betting site (using virtual currency, ie. no cash out) to bet on M.U.G.E.N bots. The goal of this bot is to:

1. Collect data about the fights and store them in a Data Mart
1. Query a database wrapper who will make decisions on the probably outcome of the fight
1. Advise on whether or not you should be and potentially how much you should bet (%-based)

---

## Components

### Database Wrapper

Currently `db-wrapper` is the wrapper for the database. As of now it will query the databse for storing incoming data sent to it by the bot that reads the chat and gets input data about the fights.

Goals for `db-wrapper`:

- Clean up the implementation
- Once data sufficient create a way to determine probably outcomes in a reasonable fashion

### Extension

Initially I was using this to feed in data from the fight to the database. However there were some drawbacks with this implementation.

- Depends on someone actually opening up a window and running salty bets
- There was a lot of information not displayed on the homepage of Salty Bets including:
    - Tier of the fight
    - Other potential fun data points (current stage, music playing, etc...)

In addition. I though of using this to be able to collect data from the Twitch chat `iframe` but since the `iframe` originates from a different URL it is impossible due to security concerns to open this up to scripts.

Goals for `extension`:

- Use it to implement automatic betting by querying the `db-wrapper` with the current fighters
    - It is nice since there exists code in there right now where I can easily get the current fight format and who is fighting. So simple uncommenting followed by a POST request to the wrapper in the future is all that's needed

### Twitch-Bot

This is the final solution to my problems. This bot will read the saltybet twitch chat. Ignoring all other users except `waif4u` who is  abot that consistently writes out the status of the current fights. The bot pulls in data from this and sends completed information in the form of a POST request to the local server to add it into the database

Goals for `twitch-bot`:

- Clean up implementation (really ugly atm)

---

## Cron Shenangians

I should probably move this off cron to a kubernetes instance

---

## Goals for the Future

The first step right now will be to understand who has the best chance of winning so obtaining as much data as possible is the priority. However there are 3 formats in SaltyBets: matchmaking, tournaments, and exhibitions. 

Matchmaking will be essentially what version 1.0 betting procedures will assume. This would be "given fighter X against fighter Y who has the highest probability of winning with what confidence?".

However later I would like to implement a higher form of this on Tournament matchmaking. Since Tournament matchmaking has the same roster of 16 characters that fight in Bo1 matches. We can potentially infer some additional dimensions of how well a fighter will do in the tournament!

Exhibitions are a crapshot. Since team names always change etc... I might have them added for fun but are low on the priority list.

Potential longshot future goals would be move from a mathematical prediction method to a machine learning method. This could either warrent a new repo using the same data or simply a different query point on the `db-wrapper`.

