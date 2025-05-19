from predictor.feature_engineering import build_match_dataframe, compute_team_strengths
from models.match import Match
from predictor.models import poisson_prob_matrix, compute_1x2_prob, compute_btts, compute_over25
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd

def predict_next_matches(session: Session):
    df = build_match_dataframe(session)
    if df.empty:
        return pd.DataFrame()
    strengths = compute_team_strengths(df)

    upcoming = session.query(Match).filter(
        Match.status != "FINISHED",
        Match.utcDate >= datetime.utcnow(),
        Match.utcDate <= datetime.utcnow() + timedelta(days=7)
    ).all()

    predictions = []

    for m in upcoming:
        h, a = m.home_team_id, m.away_team_id
        hs = strengths.get(h, {"attack_strength": 1.0, "defense_weakness": 1.0})
        as_ = strengths.get(a, {"attack_strength": 1.0, "defense_weakness": 1.0})

        lambda_h = hs["attack_strength"] * as_["defense_weakness"]
        lambda_a = as_["attack_strength"] * hs["defense_weakness"]

        matrix = poisson_prob_matrix(lambda_h, lambda_a)
        home, draw, away = compute_1x2_prob(matrix)
        btts_yes, btts_no = compute_btts(matrix)
        over, under = compute_over25(matrix)

        predictions.append({
            "match_id": m.id,
            "utcDate": m.utcDate,
            "league_id": m.league_id,
            "home_team": h,
            "away_team": a,
            "1_ODDS": round(100 / (home * 100), 2) if home > 0 else None,
            "X_ODDS": round(100 / (draw * 100), 2) if draw > 0 else None,
            "2_ODDS": round(100 / (away * 100), 2) if away > 0 else None,
            "BTTS_YES_ODDS": round(100 / (btts_yes * 100), 2) if btts_yes > 0 else None,
            "BTTS_NO_ODDS": round(100 / (btts_no * 100), 2) if btts_no > 0 else None,
            "OVER_ODDS": round(100 / (over * 100), 2) if over > 0 else None,
            "UNDER_ODDS": round(100 / (under * 100), 2) if under > 0 else None,
        })

    return pd.DataFrame(predictions)
