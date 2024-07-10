class Event:
    def __init__(self, id):
        self.id = id
        self.get_event()
        self.get_teams()
        self.get_match_info()
        self.get_team_statistics_event()
        self.get_players_statistics_event()
        self.get_shotmap_event()

    def get_event(self):
        url = get_api_url() + f'event/{self.id}'
        event = read_api_sofascore(url, selenium=False)
        self.event = event['event']
        self.season_id = self.event['season']['id']
        self.tournament_id = self.event['tournament']['uniqueTournament']['id']
        self.rodada = self.event['roundInfo']['round']
    
    def get_teams(self):
        self.home_team = Team(self.event['homeTeam']['id'], self.tournament_id, self.season_id)
        self.away_team = Team(self.event['awayTeam']['id'], self.tournament_id, self.season_id)
    
    def get_match_info(self):
        self.match_info = dict()
        self.match_info['id'] = self.id
        self.match_info['round'] = self.event['roundInfo']['round']
        self.match_info['status'] = self.event['status']['type']
        self.match_info['home_id'] = self.home_team.id
        self.match_info['home_team'] = self.home_team.name
        self.match_info['away_id'] = self.away_team.id
        self.match_info['away_team'] = self.away_team.name

        if self.match_info['status'] == 'notstarted' or self.match_info['status'] == 'postponed' or self.match_info['status'] == 'canceled':
            self.match_info['referee_id'] = None
            self.match_info['manager_home_id'] = None
            self.match_info['manager_away_id'] = None
        else:
            self.match_info['referee_id'] = self.event['referee']['id']
            self.match_info['manager_home_id'] = self.event['homeTeam']['manager']['id']
            self.match_info['manager_away_id'] = self.event['awayTeam']['manager']['id']
            
        self.match_info['date'] = datetime.fromtimestamp(self.event['startTimestamp']).strftime('%d/%m/%Y')
        self.match_info['season_id'] = self.season_id
        self.match_info['tournament_id'] = self.tournament_id
        self.match_info['city'] = self.event['venue']['city']['name']
        self.match_info['stadium'] = self.event['venue']['stadium']['name']
        print(f'Jogo: {self.home_team.name} x {self.away_team.name} - {self.rodada}ª rodada - ID: {self.id}')

    def get_team_statistics_event(self):
        print('Pegando estatísticas dos times do jogo...')
        if self.match_info['status'] == 'notstarted' or self.match_info['status'] == 'postponed' or self.match_info['status'] == 'canceled':
            return None
        else:
            url = get_api_url() + f'event/{self.id}/statistics'
            statistics_teams = read_api_sofascore(url, selenium=True, error_stop = False)
            if statistics_teams != None:
                statistics_teams = statistics_teams['statistics']
                home_stats = {'id': self.home_team.id, 'id_event': self.id, 'field':  'home'}
                away_stats = {'id': self.away_team.id, 'id_event': self.id, 'field':  'away'}
                for stat in statistics_teams:
                    period = stat['period']
                    home_period_stats = {}
                    away_period_stats = {}
                    groups = stat.get('groups', [])
                    for group in groups:
                        statistics_items = group.get('statisticsItems', [])
                        for item in statistics_items:
                            name = item.get('key')
                            home_value = item.get('homeValue')
                            away_value = item.get('awayValue')
                            
                            home_period_stats[name] = home_value
                            away_period_stats[name] = away_value
                    home_stats[period] = home_period_stats
                    away_stats[period] = away_period_stats
                teams_stats = {}
                teams_stats[home_stats['id']] = home_stats
                teams_stats[away_stats['id']] = away_stats
                self.teams_stats = teams_stats

    def get_players_statistics_event(self):
        print('Pegando estatísticas dos jogadores do jogo...')
        if self.match_info['status'] == 'notstarted' or self.match_info['status'] == 'postponed' or self.match_info['status'] == 'canceled':
            return None
        else:
            url = get_api_url() + f'event/{self.id}/lineups'
            statistics_players = read_api_sofascore(url, selenium=True, error_stop = False)
            if statistics_players != None:
                statistics_players_home = statistics_players['home']['players']
                statistics_players_away = statistics_players['away']['players']
                players_statistics = {}
                for player in statistics_players_home:
                    player_i = {}
                    has_minute_played = False
                    player_i['id'] = player['player']['id']
                    player_i['field'] = 'home' 
                    player_i['id_team'] = self.home_team.id
                    player_i['id_event'] = self.id
                    for key, value in player['statistics'].items():
                        if key != 'ratingVersions':
                            player_i[key] = value
                        if key == 'minutesPlayed':
                            has_minute_played = True
                    if has_minute_played:
                        players_statistics[player_i['id']] = player_i
                for player in statistics_players_away:
                    player_i = {}
                    has_minute_played = False
                    player_i['id'] = player['player']['id']
                    player_i['field'] = 'away' 
                    player_i['id_team'] = self.away_team.id
                    player_i['id_event'] = self.id
                    for key, value in player['statistics'].items():
                        if key != 'ratingVersions':
                            player_i[key] = value
                        if key == 'minutesPlayed':
                            has_minute_played = True
                    if has_minute_played:
                        players_statistics[player_i['id']] = player_i
                self.players_statistics = players_statistics

    def get_shotmap_event(self):
        print('Pegando informações do shotmap do jogo...')
        if self.match_info['status'] == 'notstarted' or self.match_info['status'] == 'postponed' or self.match_info['status'] == 'canceled':
            return None
        else:
            url = get_api_url() + f'event/{self.id}/shotmap'
            shotmap = read_api_sofascore(url, selenium=True, error_stop = False)['shotmap']
            if shotmap != None:
                shotmap_info = {}
                for shot in shotmap:
                    id_player = shot['player']['id']
                    id_event = self.id
                    
                    isHome = shot['isHome']
                    
                    if isHome:
                        id_team = self.home_team.id
                    else:
                        id_team = self.away_team.id
                   
                    metrics = ['isHome','xg', 'shotType', 'xgot', 'goalMouthLocation', 'situation', 'time', 'addedTime', 'bodyPart',
                               'playerCoordinates', 'goalType']
                    for metric in metrics:
                        if metric not in shot:
                            if metric == 'addedTime':
                                shot[metric] = 0
                            elif metric == 'goalType':
                                shot[metric] = 'normal'
                            else:
                                shot[metric] = None

                    xg = shot['xg']
                    shotType = shot['shotType']
                    bodypart = shot['bodyPart']
                    xgot = shot['xgot']
                    goalType = shot['goalType']

                    goalMouthLocation = shot['goalMouthLocation']
                    situation = shot['situation']
                    time = shot['time']
                    addedTime = shot['addedTime']

                    
                    if time > 45:
                        period = '2ND'
                    else:
                        period = '1ST'
                    time = time + addedTime

                    playerCoordinates = shot['playerCoordinates']
                    box_coords = {'x':{'start': 0, 'end': 17},
                                'y':{'start': 21, 'end': 79}}
                    if playerCoordinates['x'] >= box_coords['x']['start'] and playerCoordinates['x'] <= box_coords['x']['end'] and playerCoordinates['y'] >= box_coords['y']['start'] and playerCoordinates['y'] <= box_coords['y']['end']:
                        box = True
                    else:
                        box = False
                        
                    shotmap_info[shot['id']] = {'id': id_player, 'id_team': id_team, 'id_event': id_event,
                                            'shotType': shotType, 'goalType': goalType,'xg': xg, 'xgot': xgot, 'situation': situation, 'bodypart': bodypart,
                                                'playerCoordinates': playerCoordinates, 'inBox':box, 'goalMouthLocation': goalMouthLocation,
                                                'time': time, 'period': period}
                self.shotmap_info = shotmap_info

    def __str__(self):
        return f'Jogo: {self.home_team.name} x {self.away_team.name} - {self.rodada}ª rodada - ID: {self.id}'