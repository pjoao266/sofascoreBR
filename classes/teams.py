import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore
from SQLconfig.config_mysql import mydb

class Team:
    def __init__(self, id, tournament_id, season_id):
        self.id = id
        self.tournament_id = tournament_id
        self.season_id = season_id
        self.get_infos_team()
        
    def get_infos_team(self):
        url = get_api_url() + f"team/{self.id}"
        infos_team = read_api_sofascore(url, selenium=False)
        self.name = infos_team['team']['name']
        if self.tournament_id == None or self.season_id == None:
            self.tournament_id = infos_team['team']['primaryUniqueTournament']['id']
            url = get_api_url() + f"unique-tournament/{self.tournament_id}/seasons"
            infos_tournament = read_api_sofascore(url, selenium=False)['seasons']
            self.season_id = infos_tournament[0]['id']
    def save(self, mydb):
        sql = f"INSERT INTO team (id, name, id_tournament, id_season) VALUES (%s, %s, %s, %s)"
        val = (int(self.id), self.name, int(self.tournament_id), int(self.season_id))
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        
    def __str__(self):
        return f"Team: {self.name} - ID: {self.id} - Tournament ID: {self.tournament_id} - Season ID: {self.season_id}"