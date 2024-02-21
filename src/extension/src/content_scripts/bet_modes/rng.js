/**
 * RNG Betting Strategy
 *
 * Author: Francisco
 *
 * Goes all in based off of a coin flip
 */

function rngBet(matchData) {
    return {
        colour: Math.random() < 0.5 ? 'red' : 'blue',
        confidence: 1,
    }
}

export { rngBet as default }
