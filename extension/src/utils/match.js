function calculateRedVsBlueMatchData(matches, fighterRedId, fighterBlueId) {
  let redWinsVsBlue = 0
  let redMatchesVsBlue = 0
  let redBetVsBlue = 0
  let blueBetVsRed = 0
  for (const match of matches) {
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

  return {
    redWinsVsBlue: redWinsVsBlue,
    redMatchesVsBlue: redMatchesVsBlue,
    redBetVsBlue: redBetVsBlue,
    blueBetVsRed: blueBetVsRed
  }
}

export {
  calculateRedVsBlueMatchData
}