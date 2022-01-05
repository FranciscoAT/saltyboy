/**
 * Elo Tier Betting Strategy
 *
 * Author: Francisco
 *
 * Bets using the tiered ELO. If equivalently matched will tie break based on average bet.
 * If either fighter have no data will bet $1 on red.
 */

function eloTierBet(matchData) {
    let betData = {
        colour: 'red',
        confidence: null,
    }

    let fighterRedInfo = matchData.fighter_red_info
    let fighterBlueInfo = matchData.fighter_blue_info
    if (fighterRedInfo == null || fighterBlueInfo == null) {
        return betData
    }

    let redWinConfidence =
        1 -
        1 /
            (1 +
                Math.pow(
                    10,
                    (fighterRedInfo.tier_elo - fighterBlueInfo.tier_elo) / 400
                ))
    if (redWinConfidence < 0.5) {
        betData.colour = 'blue'
        betData.confidence = 1 - redWinConfidence
    } else if (redWinConfidence == 0.5) {
        betData.confidence = 0.5
        if (fighterRedInfo.average_bet < fighterBlueInfo.average_bet) {
            betData.colour = 'blue'
        }
    } else {
        betData.confidence = redWinConfidence
    }

    return betData
}

export { eloTierBet as default }
