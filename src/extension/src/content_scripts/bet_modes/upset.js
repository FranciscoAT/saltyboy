/**
 * Upset Betting Strategy (Naive modification)
 *
 * Author: Francisco, modified by Rei for upsets by simple color swap for results.
 *
 * Basis the bet on previous win-rates and average bets.
 * If either fighter has no info will return a null confidence.
 * Otherwise if both fighters have fought before it will the one with
 * the higher win rate against the other.
 * Then if neither have fought each other it will pick the one with the best
 * overall win rate. If there is a tie between their win-rates it will pick
 * the one with the highest average bet.
 * It then bets against the color that is rated to win.
 *
 * Confidence is based off of their win rates.
 * Eg. two fighters with the same win rate against each other will return a
 * confidence of 0.5 betting with the one with the higher average bet.
 */

import { calculateRedVsBlueMatchData } from '../../utils/match'

function upsetBet(matchData) {
    let betData = {
        colour: 'red',
        confidence: null,
    }

    let fighterRedInfo = matchData.fighter_red_info
    let fighterBlueInfo = matchData.fighter_blue_info
    if (fighterRedInfo == null || fighterBlueInfo == null) {
        return betData
    }

    // Upset betting on matches of Red vs Blue
    let redVsBlueMatchData = calculateRedVsBlueMatchData(
        fighterRedInfo.matches,
        fighterRedInfo.id,
        fighterBlueInfo.id
    )
    let redWinsVsBlue = redVsBlueMatchData.redWinsVsBlue
    let redMatchesVsBlue = redVsBlueMatchData.redMatchesVsBlue
    let redBetVsBlue = redVsBlueMatchData.redBetVsBlue
    let blueBetVsRed = redVsBlueMatchData.blueBetVsRed

    if (redMatchesVsBlue > 0) {
        let redWinRateVsBlue = redWinsVsBlue / redMatchesVsBlue
        if (redWinRateVsBlue < 0.5) {
            betData.colour = 'red'
            betData.confidence = 1 - redWinRateVsBlue
        } else if (redWinRateVsBlue == 0.5) {
            let redAverageBetVsBlue = redBetVsBlue / redMatchesVsBlue
            let blueAverageBetVsRed = blueBetVsRed / redMatchesVsBlue
            betData.confidence = 0.5
            if (blueAverageBetVsRed > redAverageBetVsBlue) {
                betData.colour = 'red'
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
            fighterRedInfo.stats.average_bet < fighterBlueInfo.stats.average_bet
        ) {
            betData.colour = 'red'
        }
    } else if (blueWinRate > redWinRate) {
        betData.confidence = blueWinRate / (redWinRate + blueWinRate)
        betData.colour = 'red'
    } else {
        betData.confidence = redWinRate / (redWinRate + blueWinRate)
    }

    return betData
}

export { upsetBet as default }
