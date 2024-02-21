/**
 * Passive Betting Strategy
 *
 * Author: Francisco
 *
 * Will always bet $1 on Red.
 */

function passiveBet(matchData) {
    return {
        colour: 'red',
        confidence: null,
    }
}

export { passiveBet as default }
