from classes.utils import get_api_url, read_api_sofascore # Import the get_api_url function from vars/global.py
import requests # Import the requests module
import pandas as pd
from classes.teams import Team


class Tournament:
    def __init__(self, id, year):
        self.id = id
        self.year = year
        self.get_tournament()
        self.get_tournament_seasons()
        self.get_season_by_year(self.year)
        self.get_teams_tournament()
        self.get_standings()

    def get_tournament(self):
        url = get_api_url() + 'unique-tournament/{id}'.format(id=self.id)
        data_tournament = read_api_sofascore(url, selenium=False)
        self.name = data_tournament['uniqueTournament']['name']
        self.country = data_tournament['uniqueTournament']['category']['country']['name']
    
    def get_tournament_seasons(self):
        url = get_api_url() + f'unique-tournament/{self.id}/seasons/'
        seasons = read_api_sofascore(url, selenium=False)
        df_seasons = pd.DataFrame(seasons['seasons'])
        self.df_seasons = df_seasons[['name', 'year', 'id']]
    
    def get_season_by_year(self, year):
        try:
            self.season_id = self.df_seasons[self.df_seasons['year'] == str(year)]['id'].values[0]
        except IndexError:
            self.season_id = ''
        url = get_api_url() + f'unique-tournament/{self.id}/season/{self.season_id}/teams'
        self.season_info = read_api_sofascore(url, selenium=False)

    def get_teams_tournament(self):
        teams = dict()
        for team in self.season_info['teams']:
            teams[team['id']] = Team(team['id'], team['name'], self.id, self.season_id)
        self.teams = teams
    
    def get_standings(self):
        url = get_api_url() + f'unique-tournament/{self.id}/season/{self.season_id}/standings/total'
        standings = read_api_sofascore(url)
        standings = standings['standings'][0]['rows']
        statitics_table = pd.DataFrame()
        for time in standings:
            time_id = time['team']['id']
            time_position = time['position']
            time_points = time['points']
            time_jogos = time['matches']

            team_brasileirao = self.teams.get(time_id)
            team_brasileirao.points = time_points
            team_brasileirao.position = time_position
            team_brasileirao.matches = time_jogos
            statitics_table_time = pd.DataFrame([(team_brasileirao.id, team_brasileirao.name,
                                                team_brasileirao.position, team_brasileirao.points,
                                                team_brasileirao.matches)],
                                                columns=['id', 'team', 'position', 'points', 'matches'])
            statitics_table = pd.concat([statitics_table, statitics_table_time])
        self.standing = statitics_table.sort_values('position', ascending=True)       
        
    def __str__(self) -> str:
        return f'Tournament: {self.name} - Country: {self.country} - Year: {self.year}'
            
