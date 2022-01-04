/**
 * Naive betting Strategy
 *
 * Basis the bet on previous win-rates and average bets.
 * If either fighter has no info will return a null confidence.
 * Otherwise if both fighters have fought before it will take the one with
 * the higher win rate against the other.
 * Then if neither have fought each other it will pick the one with the best
 * overall win rate. If there is a tie between their win-rates it will pick
 * the one with the highest average bet.
 *
 * Confidence is based off of their win rates.
 * Eg. two fighters with the same win rate against each other will return a
 * confidence of 0.5 betting with the one with the higher average bet.
 */

function naiveBet(matchData) {
    let betData = {
        colour: 'red',
        confidence: null,
    }

    let fighterRedInfo = matchData.fighter_red_info
    let fighterBlueInfo = matchData.fighter_blue_info
    if (fighterRedInfo == null || fighterBlueInfo == null) {
        return betData
    }

    let fighterRedId = fighterRedInfo.id
    let fighterBlueId = fighterBlueInfo.id

    // Base betting on matches of Red vs Blue
    let redWinsVsBlue = 0
    let redMatchesVsBlue = 0
    let redBetVsBlue = 0
    let blueBetVsRed = 0
    for (const match of fighterRedInfo.matches) {
        if (
            (match.fighter_red == fighterRedId &&
                match.fighter_blue == fighterBlueId) ||
            (match.fighter_red == fighterBlueId &&
                match.fighter_blue == fighterRedId)
        ) {
            if (match.winner == fighterRedId) {
                redWinsVsBlue += 1
            }
            redMatchesVsBlue += 1
            if (match.fighter_red == fighterRedId) {
                redBetVsBlue += match.bet_red
                blueBetVsRed += match.bet_blue
            } else {
                redBetVsBlue += match.bet_blue
                blueBetVsRed += match.bet_red
            }
        }
    }

    if (redMatchesVsBlue > 0) {
        let redWinRateVsBlue = redWinsVsBlue / redMatchesVsBlue
        if (redWinRateVsBlue < 0.5) {
            betData.colour = 'blue'
            betData.confidence = 1 - redWinRateVsBlue
        } else if (redWinRateVsBlue == 0.5) {
            let redAverageBetVsBlue = redBetVsBlue / redMatchesVsBlue
            let blueAverageBetVsRed = blueBetVsRed / redMatchesVsBlue
            betData.confidence = 0.5
            if (blueAverageBetVsRed > redAverageBetVsBlue) {
                betData.colour = 'blue'
            }
        } else {
            betData.confidence = redWinRateVsBlue
        }
        return betData
    }

    // Base betting on average stats
    let redWinRate = fighterRedInfo.stats.win_rate
    let blueWinRate = fighterBlueInfo.stats.win_rate

    if (redWinRate == blueWinRate) {
        betData.confidence = 0.5
        if (
            fighterRedInfo.stats.average_bet <
            fighterBlueInfo.stats.average_bet
        ) {
            betData.colour = 'blue'
        }
    } else if (blueWinRate > redWinRate) {
        betData.confidence = blueWinRate / (redWinRate + blueWinRate)
        betData.colour = 'blue'
    } else {
        betData.confidence = redWinRate / (redWinRate + blueWinRate)
    }

    return betData
}

export { naiveBet as default }
