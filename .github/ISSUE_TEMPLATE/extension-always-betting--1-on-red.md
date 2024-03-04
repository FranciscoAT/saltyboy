---
name: Extension always betting $1 on Red
about: If the bot betting $1 on Red consistently
title: ''
labels: ''
assignees: ''

---

### Please Read

Before submitting this issue please be aware of the following. The upstream bot which updates the SaltyBoy API can get out of date. Resulting in the extension betting $1 on Red. If this happens confirm the following:

- It is possible Waif4U is not active in the Twitch chat. SaltyBoy reads Waif4U's messages to determine and update the state of matches. If that Twitch bot is down SaltyBoy will not update.
- It is possible that for a given match the extension bets $1 on red because Waif4U did not announce the "Bets Open..." message. If this is the case wait for a new match and confirm that Waif4U announces in the chat "Bets Open...". If the extension still bets $1 on Red please read next steps.
- The worst case downtime in the even the Bot connecting to the SaltyBet IRC Twitch channel can be down for before recovery kicks in is up to 10 minutes.

Therefore, if you've verified that:

- Waif4U is announcing the "Bets Open" message in chat. And,
- The extension has been betting $1 on Red for more than 10 minutes. Then,
- You may submit this issue.

### Issue

- [ ] I have read and understood the above [Please Read](#please-read) section.
- [ ] I confirmed that Waif4u is announcing the "Bet Open" messages in Twitch chat.
- [ ] I confirmed that my extension has been betting $1 on Red consistently.
- [ ] I have read and am prepared to provide any debugging information upon request. See [HOWTO: Debugging](https://github.com/FranciscoAT/saltyboy/wiki/HOWTO:-Debugging#dump-settings).
