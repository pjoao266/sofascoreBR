
import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore
from classes.teams import Team
from SQLconfig.config_mysql import mydb

class Event:
    """
    Represents a sports event.

    Attributes:
    - id: The ID of the event.
    - event: The event data retrieved from the API.
    - season_id: The ID of the season the event belongs to.
    - tournament_id: The ID of the tournament the event belongs to.
    - rodada: The round number of the event.
    - home_team: The home team of the event.
    - away_team: The away team of the event.
    - match_info: Information about the match.
    - teams_stats: Statistics of the teams in the match.
    - players_statistics: Statistics of the players in the match.
    """

    def __init__(self, id):
        """
        Initializes a new instance of the Event class.

        Parameters:
        - id: The ID of the event.
        """
        self.id = id

    def run(self):
        """
        Runs the event processing logic.
        """
        self.get_event()
        self.get_teams()
        self.get_match_info()
        if self.match_info['status'] == 'finished':
            self.get_team_statistics_event()
            self.get_players_statistics_event()
            self.get_shotmap_event()

    def get_event(self):
        """
        Retrieves the event data from the API.
        """
        url = get_api_url() + f'event/{self.id}'
        event = read_api_sofascore(url, selenium=False)
        self.event = event['event']
        self.season_id = self.event['season']['id']
        self.tournament_id = self.event['tournament']['uniqueTournament']['id']
        self.rodada = self.event['roundInfo']['round']
    
    def get_teams(self):
        """
        Retrieves the home and away teams of the event.
        """
        self.home_team = Team(self.event['homeTeam']['id'], self.tournament_id, self.season_id)
        self.home_team.get_infos_team()
        self.away_team = Team(self.event['awayTeam']['id'], self.tournament_id, self.season_id)
        self.away_team.get_infos_team()

    
    def get_match_info(self):
        """
        Retrieves information about the match.
        """
        self.match_info = dict()
        self.match_info['id'] = self.id
        self.match_info['round'] = self.event['roundInfo']['round']
        self.match_info['status'] = self.event['status']['type']
        self.match_info['home_id'] = self.home_team.id
        self.match_info['home_team'] = self.home_team.name
        self.match_info['away_id'] = self.away_team.id
        self.match_info['away_team'] = self.away_team.name

        if self.match_info['status'] != 'finished':
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
        """
        Retrieves the statistics of the teams in the match.
        """
        print('Pegando estatísticas dos times do jogo...')
        if self.match_info['status'] != 'finished':
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
        """
        Retrieves the statistics of the players in the match.
        """
        print('Pegando estatísticas dos jogadores do jogo...')
        if self.match_info['status'] != 'finished':
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

    def get_importance_of_goals(self, shotmap_info):
        """
        Calculates the importance of goals in the shotmap.

        Parameters:
        - shotmap_info: The shotmap information.

        Returns:
        - The shotmap information with the importance of goals added.
        """
        shot_goals = dict()
        for key, shot in shotmap_info.items():
            if shot['shotType'] == 'goal':
                shot_goals[key] = shot
                shot_goals[key]['id_key'] = key
        sorted_shot_goals = sorted(shot_goals.values(), key=lambda x: x['time_seconds'])
        n_gols = len(sorted_shot_goals)
        home_goals = 0
        away_goals = 0
        cont_goals = 0
        for goals in sorted_shot_goals:
            cont_goals +=1
            if goals['id_team'] == self.home_team.id:
                home_goals += 1
                goals_favor = home_goals
                goals_against = away_goals
            else:
                away_goals += 1
                goals_favor = away_goals
                goals_against = home_goals
            goal_to_ahead_score = False
            goal_to_open_score = False
            goal_to_tie = False
            goal_winning = False
            goal_to_save_lose = False

            if goals_favor-1==goals_against:
                goal_to_ahead_score = True
                if goals_favor == 1:
                    goal_to_open_score = True
                if cont_goals == n_gols:
                    goal_winning = True
            elif goals_favor == goals_against:
                goal_to_tie = True
                if cont_goals == n_gols:
                    goal_to_save_lose = True
            score_after_goal = goals_favor - goals_against

            shotmap_info[goals['id_key']]['score_after_goal'] = score_after_goal
            shotmap_info[goals['id_key']]['goal_to_ahead_score'] = goal_to_ahead_score
            shotmap_info[goals['id_key']]['goal_to_open_score'] = goal_to_open_score
            shotmap_info[goals['id_key']]['goal_to_tie'] = goal_to_tie
            shotmap_info[goals['id_key']]['goal_winning'] = goal_winning
            shotmap_info[goals['id_key']]['goal_to_save_lose'] = goal_to_save_lose
            
        return shotmap_info
        
    def get_shotmap_event(self):
        """
        Retrieves the shotmap information of the match.
        """
        print('Pegando informações do shotmap do jogo...')
        if self.match_info['status'] != 'finished':
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
                        # Process metric data
                        pass
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
                    time_seconds = shot['timeSeconds']
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
                                                'time': time, 'time_seconds': time_seconds, 'period': period}
                self.shotmap_info = self.get_importance_of_goals(shotmap_info)
                self.get_goals_info()


    def get_goals_info(self):
        """
        Retrieves information about the goals scored in the match.
        """
        shot_goals = dict()
        for key, shot in self.shotmap_info.items():
            if shot['shotType'] == 'goal':
                shot_goals[key] = shot

        home_goals = 0
        away_goals = 0
        home_goals_1st_period = 0
        home_goals_2nd_period = 0
        away_goals_1st_period = 0
        away_goals_2nd_period = 0

        for key, shot in shot_goals.items():
            if shot['period'] == '1ST':
                if shot['id_team'] == self.home_team.id:
                    home_goals_1st_period += 1
                else:
                    away_goals_1st_period += 1
            elif shot['period'] == '2ND':
                if shot['id_team'] == self.home_team.id:
                    home_goals_2nd_period += 1
                else:
                    away_goals_2nd_period += 1
            
            if shot['id_team'] == self.home_team.id:
                home_goals += 1
            else:
                away_goals += 1
                
        self.match_info['score_home'] = home_goals
        self.match_info['score_away'] = away_goals

        if 'teams_stats' in self.__dict__:
            self.teams_stats[self.home_team.id]['ALL']['goals'] = home_goals
            self.teams_stats[self.away_team.id]['ALL']['goals'] = away_goals
            self.teams_stats[self.home_team.id]['1ST']['goals'] = home_goals_1st_period
            self.teams_stats[self.away_team.id]['1ST']['goals'] = away_goals_1st_period
            self.teams_stats[self.home_team.id]['2ND']['goals'] = home_goals_2nd_period
            self.teams_stats[self.away_team.id]['2ND']['goals'] = away_goals_2nd_period
            
        self.goals_info = {
            'ALL': {'home': home_goals, 'away': away_goals},
            '1ST': {'home': home_goals_1st_period, 'away': away_goals_1st_period},
            '2ND': {'home': home_goals_2nd_period, 'away': away_goals_2nd_period}
        }

    def save(self, mydb):
        """
        Saves the event to the database.
        Parameters:
        - mydb: The MySQL database connection object.
        """

        sql_check = "SELECT * FROM matches WHERE id = %s AND id_tournament = %s AND id_season = %s"
        val_check = (int(self.id), int(self.match_info['tournament_id']), int(self.match_info['season_id']))
        mycursor = mydb.cursor()
        mycursor.execute(sql_check, val_check)
        myresult = mycursor.fetchall()
        mycursor.close()
        if len(myresult) > 0:
            sql = "UPDATE matches SET id_team_home = %s, id_team_away = %s, rodada = %s, status = %s, referee_id = %s, manager_home_id = %s, manager_away_id = %s, date = %s, city = %s, stadium = %s, home_goals = %s, away_goals = %s, dt_insertion = %s WHERE id = %s AND id_tournament = %s AND id_season = %s"
        else:
            sql = "INSERT INTO matches (id, id_team_home, id_team_away, id_tournament, id_season, rodada, status, referee_id, manager_home_id, manager_away_id, date, city, stadium, home_goals, away_goals)\
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        int_vars = ['id', 'id_team_home', 'id_team_away', 'id_tournament', 'id_season',
        'rodada', 'referee_id', 'manager_home_id', 'manager_away_id', 'score_home', 'score_away']
        for var in int_vars:
            if var in self.match_info.keys() and self.match_info[var] != None:
                self.match_info[var] = int(self.match_info[var])
            else:
                self.match_info[var] = None
        date_info = datetime.strptime(self.match_info['date'], "%d/%m/%Y")
        if len(myresult) > 0:
            val = (self.match_info['home_id'], self.match_info['away_id'], self.match_info['round'], self.match_info['status'], self.match_info['referee_id'],
                self.match_info['manager_home_id'], self.match_info['manager_away_id'],
                date_info, self.match_info['city'], self.match_info['stadium'],
                self.match_info['score_home'], self.match_info['score_away'], datetime.now(),
                self.id, self.match_info['tournament_id'], self.match_info['season_id'])
        else:
            val = (self.id, self.match_info['home_id'], self.match_info['away_id'], self.match_info['tournament_id'], self.match_info['season_id'],
                self.match_info['round'], self.match_info['status'], self.match_info['referee_id'],
                self.match_info['manager_home_id'], self.match_info['manager_away_id'],
                date_info, self.match_info['city'], self.match_info['stadium'],
                self.match_info['score_home'], self.match_info['score_away'])
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        
    def __str__(self):
        if 'goals_info' in self.__dict__:
            return f'Jogo: {self.home_team.name} {self.goals_info["ALL"]["home"]} x {self.goals_info["ALL"]["away"]} {self.away_team.name} - {self.rodada}ª rodada - ID: {self.id}'
        else:
            return f'Jogo: {self.home_team.name} x {self.away_team.name} - {self.rodada}ª rodada - ID: {self.id}'