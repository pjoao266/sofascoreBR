from classes.utils import get_api_url, read_api_sofascore # Import the get_api_url function from vars/global.py
import requests # Import the requests module
import pandas as pd
from classes.tournaments import Tournament
from classes.players import Player

class Team:
    def __init__(self, id, name, tournament_id, season_id):
        self.id = id
        if name == None or tournament_id == None or season_id == None:
            self.get_infos_team()
        else:
            self.name = name
            self.tournament_id = tournament_id
            self.season_id = season_id
        
    def get_infos_team(self):
        url = get_api_url() + f"team/{self.id}"
        infos_team = read_api_sofascore(url, selenium=False)
        self.name = infos_team['team']['name']
        self.tournament_id = infos_team['team']['primaryUniqueTournament']['id']
        torneio = Tournament(id = self.tournament_id, year = None)
        max_year_season = torneio.df_seasons['year'].max()
        self.season_id = torneio.df_seasons[torneio.df_seasons['year'] == max_year_season]['id'].values[0]
    
    def __str__(self):
        return f"Team: {self.name} - ID: {self.id} - Tournament ID: {self.tournament_id} - Season ID: {self.season_id}"