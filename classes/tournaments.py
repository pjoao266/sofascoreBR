class Tournament:
    def __init__(self, id, year):
        self.id = id
        self.year = year
        self.get_tournament()
        self.get_tournament_seasons()

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
            teams[team['id']] = Team(team['id'], self.id, self.season_id)
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
    def get_events_rodada(self, rodada):
        url = get_api_url() + f'unique-tournament/{self.id}/season/{self.season_id}/events/round/{rodada}'
        events = read_api_sofascore(url, selenium=False)
        jogos_rodada = events['events']
        return jogos_rodada
    
    def get_events(self):
        jogos = dict()
        for i in range(38):
            rodada = i + 1
            jogos_rodada = self.get_events_rodada(rodada)
            for event in jogos_rodada:
                event_id = event['id']
                evento_i = Event(event_id)
                jogos[event_id] = evento_i
        self.jogos = jogos

    def get_table_of_events(self):
        table = pd.DataFrame()
        for key, value in self.jogos.items():
            table = pd.concat([table, pd.DataFrame(value.match_info, index=[0])])
        return table  
    
    def run(self):
        print('Pegando informações do torneio...')
        self.get_season_by_year(self.year)
        self.get_teams_tournament()
        print('Calculando tabela do torneio...')
        self.get_standings()
        print('Pegando informações de eventos do torneio...')
        self.get_events()

    def __str__(self) -> str:
        return f'Tournament: {self.name} - Country: {self.country} - Year: {self.year}'