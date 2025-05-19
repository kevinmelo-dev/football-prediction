import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": os.getenv("API_TOKEN")}


def fetch_league(code):
    return requests.get(f"{BASE_URL}/competitions/{code}", headers=HEADERS).json()

def fetch_teams(code):
    return requests.get(f"{BASE_URL}/competitions/{code}/teams", headers=HEADERS).json()

def fetch_matches(code, season):
    return requests.get(f"{BASE_URL}/competitions/{code}/matches?season={season}", headers=HEADERS).json()
