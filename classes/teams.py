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
            torneio = Tournament(id = self.tournament_id, year = None)
            max_year_season = torneio.df_seasons['year'].max()
            self.season_id = torneio.df_seasons[torneio.df_seasons['year'] == max_year_season]['id'].values[0]
    
    def __str__(self):
        return f"Team: {self.name} - ID: {self.id} - Tournament ID: {self.tournament_id} - Season ID: {self.season_id}"