from sqlalchemy.orm import Session
from models.match import Match
import pandas as pd
from collections import defaultdict

def build_match_dataframe(session: Session):
    matches = session.query(Match).filter(Match.status == "FINISHED").all()
    data = [{
        "match_id": m.id,
        "season": m.season,
        "utcDate": m.utcDate,
        "matchday": m.matchday,
        "home_team": m.home_team_id,
        "away_team": m.away_team_id,
        "home_goals": m.home_score,
        "away_goals": m.away_score
    } for m in matches]
    return pd.DataFrame(data)


def compute_team_strengths(df, recent_matches=10):
    teams = set(df["home_team"]).union(df["away_team"])
    strength = {}

    for team_id in teams:
        home_games = df[df["home_team"] == team_id].sort_values("utcDate", ascending=False).head(recent_matches)
        away_games = df[df["away_team"] == team_id].sort_values("utcDate", ascending=False).head(recent_matches)

        total_goals_scored = (
            home_games["home_goals"].sum() +
            away_games["away_goals"].sum()
        )
        total_goals_conceded = (
            home_games["away_goals"].sum() +
            away_games["home_goals"].sum()
        )
        total_matches = len(home_games) + len(away_games)

        strength[team_id] = {
            "attack_strength": total_goals_scored / total_matches if total_matches > 0 else 1.0,
            "defense_weakness": total_goals_conceded / total_matches if total_matches > 0 else 1.0
        }

    return strength
