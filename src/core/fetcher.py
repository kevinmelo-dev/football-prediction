import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert

from api.football_data_api import fetch_league, fetch_teams, fetch_matches
from db.database import SessionLocal, engine
from models.base import Base
from models.league import League
from models.match import Match
from models.team import Team

load_dotenv()
Base.metadata.create_all(bind=engine)

def upsert(session, model, data, key="id"):
    stmt = insert(model).values(data)
    stmt = stmt.on_conflict_do_update(
        index_elements=[key],
        set_={c.name: getattr(stmt.excluded, c.name) for c in stmt.table.columns if c.name != key}
    )
    session.execute(stmt)

def run_fetch():
    leagues = os.getenv("LEAGUES").split(",")
    seasons = os.getenv("SEASONS").split(",")

    session = SessionLocal()

    for league_code in leagues:
        league_data = fetch_league(league_code)
        league = {
            "id": league_data["id"],
            "name": league_data["name"],
            "code": league_data["code"],
            "country": league_data["area"]["name"],
            "emblem": league_data.get("emblem", "")
        }
        upsert(session, League, league)

        team_data = fetch_teams(league_code).get("teams", [])
        for t in team_data:
            team = {
                "id": t["id"],
                "name": t["name"],
                "shortName": t["shortName"],
                "tla": t["tla"],
                "crest": t["crest"]
            }
            upsert(session, Team, team)

        for season in seasons:
            match_response = fetch_matches(league_code, season)
            matches = match_response.get("matches")

            if not matches:
                print(f"⚠️  Sem dados para {league_code} na temporada {season}. Ignorando.")
                continue

            for m in matches:
                home_id = m["homeTeam"]["id"]
                away_id = m["awayTeam"]["id"]

                for team_id in [home_id, away_id]:
                    if not session.query(Team).filter(Team.id == team_id).first():
                        team = Team(id=team_id, name=f"Team {team_id}", shortName="", tla="", crest="")
                        session.add(team)

                match = {
                    "id": m["id"],
                    "season": season,
                    "league_id": league_data["id"],
                    "utcDate": datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00")),
                    "status": m["status"],
                    "matchday": m["matchday"],
                    "home_team_id": home_id,
                    "away_team_id": away_id,
                    "home_score": m["score"]["fullTime"]["home"],
                    "away_score": m["score"]["fullTime"]["away"],
                }
                upsert(session, Match, match)

    session.commit()
    session.close()
