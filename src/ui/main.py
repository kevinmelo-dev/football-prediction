import streamlit as st
import pandas as pd
from db.database import SessionLocal
from models.team import Team
from models.league import League
from predictor.predictor import predict_next_matches
from core.fetcher import run_fetch

st.set_page_config(page_title="Probabilidades Futebol", layout="wide")
st.title("📊 Odds Justas de Partidas (Próximos 7 dias)")

if st.button("🔄 Atualizar dados agora"):
    with st.spinner("Buscando dados da API e atualizando o banco..."):
        run_fetch()
    st.success("Dados atualizados com sucesso!")

with st.spinner("Calculando odds..."):
    session = SessionLocal()
    df = predict_next_matches(session)
    teams = {t.id: t.name for t in session.query(Team).all()}
    leagues = {l.id: l.name for l in session.query(League).all()}
    session.close()

if df.empty:
    st.warning("Nenhuma partida nos próximos 7 dias.")
    st.stop()

# Filtro de liga
df["league_id"] = df["league_id"].astype(int)
selected_league = st.selectbox("Selecione a Liga", options=[(k, v) for k, v in leagues.items()], format_func=lambda x: x[1])
df = df[df["league_id"] == selected_league[0]]

df["home_name"] = df["home_team"].map(teams)
df["away_name"] = df["away_team"].map(teams)
df["Partida"] = df["home_name"] + " vs " + df["away_name"]
df["Data"] = pd.to_datetime(df["utcDate"]).dt.strftime("%d/%m/%Y %H:%M")

df = df[[
    "Data", "Partida",
    "1_ODDS", "X_ODDS", "2_ODDS",
    "BTTS_YES_ODDS", "BTTS_NO_ODDS",
    "OVER_ODDS", "UNDER_ODDS"
]]

st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "1_ODDS": st.column_config.NumberColumn("🏠 Casa (Odds)", format="%.2f"),
        "X_ODDS": st.column_config.NumberColumn("🤝 Empate (Odds)", format="%.2f"),
        "2_ODDS": st.column_config.NumberColumn("🚗 Fora (Odds)", format="%.2f"),
        "BTTS_YES_ODDS": st.column_config.NumberColumn("🎯 Ambas Marcam: Sim", format="%.2f"),
        "BTTS_NO_ODDS": st.column_config.NumberColumn("🚫 Ambas Marcam: Não", format="%.2f"),
        "OVER_ODDS": st.column_config.NumberColumn("⬆️ Over 2.5", format="%.2f"),
        "UNDER_ODDS": st.column_config.NumberColumn("⬇️ Under 2.5", format="%.2f"),
    },
    height=600
)
