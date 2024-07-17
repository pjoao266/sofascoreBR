from datetime import datetime
import sys
sys.path.append("../")
from classes.utils import get_api_url, read_api_sofascore, db_to_excel
from classes.players import Player
from classes.teams import Team
from classes.managers import Manager
from classes.referees import Referee
from classes.events import Event
import json
import pandas as pd
from SQLconfig.config_mysql import mydb


class Tournament:
    def __init__(self, id, year):
        self.id = id
        self.year = year
        self.has_new_events = False
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
        # read teams already saved in the database
        sql_check_saved = f"SELECT id FROM team WHERE id_tournament = %s AND id_season = %s"
        val_check_saved = (int(self.id), int(self.season_id))
        mycursor = mydb.cursor()
        mycursor.execute(sql_check_saved, val_check_saved)
        id_teams_saved = mycursor.fetchall()
        mycursor.close()
        id_teams_saved = [id_team[0] for id_team in id_teams_saved]

        id_not_saved = [x['id'] for x in self.season_info['teams'] if x['id'] not in id_teams_saved]
        for team in self.season_info['teams']:
            if team['id'] in id_not_saved:
                team_class = Team(team['id'], self.id, self.season_id)
                team_class.get_infos_team()
                teams[team['id']] = team_class
            else:
                team_class = Team(team['id'], self.id, self.season_id)
                sql_get_team = f"SELECT * FROM team WHERE id = {int(team['id'])}"
                mycursor = mydb.cursor()
                mycursor.execute(sql_get_team)
                team_info = mycursor.fetchall()
                mycursor.close()
                team_info = team_info[0]
                team_class.name = team_info[1]
                teams[team['id']] = team_class
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
        sql_check_saved = f"SELECT id FROM matches WHERE id_tournament = %s AND id_season = %s AND status = 'finished'"
        val_check_saved = (int(self.id), int(self.season_id))
        mycursor = mydb.cursor()
        mycursor.execute(sql_check_saved, val_check_saved)
        id_events_saved = mycursor.fetchall()
        mycursor.close()
        id_events_saved = [id_events[0] for id_events in id_events_saved]
        jogos = dict()

        url = get_api_url() + f'unique-tournament/{self.id}/season/{self.season_id}/rounds/'
        current_round = read_api_sofascore(url, selenium=False)['currentRound']['round']

        for i in range(current_round):
            rodada = i + 1
            jogos_rodada = self.get_events_rodada(rodada)
            id_not_saved = [x['id'] for x in jogos_rodada if x['id'] not in id_events_saved]
            for event in jogos_rodada:
                if event['id'] in id_not_saved:
                    event_id = event['id']
                    evento_i = Event(event_id)
                    evento_i.run()
                    if evento_i.match_info['status'] == 'finished':
                        self.has_new_events = True
                    jogos[event_id] = evento_i
        self.jogos = jogos

    def get_table_of_events(self):
        table = pd.DataFrame()
        for key, value in self.jogos.items():
            table = pd.concat([table, pd.DataFrame(value.match_info, index=[0])])
        return table 

    def get_players(self):
        distinct_player_ids = set()
        for id_jogo, jogo in self.jogos.items():
            if jogo.match_info['status'] == 'finished':
                distinct_player_ids.update(jogo.players_statistics.keys())

        distinct_player_ids = list(distinct_player_ids)
        sql_check_saved = f"SELECT id FROM player WHERE 1"
        mycursor = mydb.cursor()
        mycursor.execute(sql_check_saved)
        myresult = mycursor.fetchall()
        id_players_saved = [x[0] for x in myresult]

        distinct_player_ids_not_saved = [x for x in distinct_player_ids if x not in id_players_saved]
        players = dict()
        cont = 1
        len_distinct_player_ids = len(distinct_player_ids_not_saved)
        for id_player in distinct_player_ids_not_saved:
                print(f'Pegando informações do jogador {id_player}... - {cont}/{len_distinct_player_ids}')
                player = Player(id_player)
                player.get_info_players()
                player.get_player_position()
                players[id_player] = player
                cont += 1
        self.players = players
    
    def get_referees(self):
        id_referees = set()
        for id_jogo, jogo in self.jogos.items():
            if jogo.match_info['status'] == 'finished':
                id_referees.add(jogo.match_info['referee_id'])
        id_referees = list(set(id_referees))

        sql_check_saved = f"SELECT id FROM referee WHERE 1"
        mycursor = mydb.cursor()
        mycursor.execute(sql_check_saved)
        myresult = mycursor.fetchall()
        id_referees_saved = [x[0] for x in myresult]

        id_referees_not_saved = [x for x in id_referees if x not in id_referees_saved]
        referees = dict()
        cont = 0
        n_referees = len(id_referees_not_saved)
        for id_referee in id_referees_not_saved:
            cont += 1
            print(f'Pegando informações do árbitro {id_referee}... - {cont}/{n_referees}')
            referee = Referee(id_referee)
            referee.get_info_referee()
            referees[id_referee] = referee
        self.referees = referees

    def get_managers(self):
        id_managers = set()
        for id_jogo, jogo in self.jogos.items():
            if jogo.match_info['status'] == 'finished':
                id_managers.add(jogo.match_info['manager_home_id'])
                id_managers.add(jogo.match_info['manager_away_id'])
        id_managers = list(set(id_managers))
        
        sql = "SELECT id FROM manager WHERE 1"
        mycursor = mydb.cursor()
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        id_managers_saved = [x[0] for x in myresult]

        id_managers_not_saved = [x for x in id_managers if x not in id_managers_saved]

        managers = dict()
        cont = 0
        n_managers = len(id_managers_not_saved)
        for id_manager in id_managers_not_saved:
            cont += 1
            print(f'Pegando informações do manager {id_manager}... - {cont}/{n_managers}')
            manager = Manager(id_manager)
            manager.get_info_manager()
            managers[id_manager] = manager
        self.managers = managers
    
    def run(self):
        print('Pegando informações do torneio...')
        self.get_season_by_year(self.year)
        self.get_teams_tournament()
        print('Calculando tabela do torneio...')
        self.get_standings()
        print('Pegando informações de eventos do torneio...')
        self.get_events()
        print('Pegando informações dos jogadores...')
        self.get_players()
        print('Pegando informações dos técnicos...')
        self.get_managers()
        print('Pegando informações dos árbitros...')
        self.get_referees()

    def get_id_db_tournament(self, mydb):
        sql_check_saved = f"SELECT id FROM tournament WHERE tournament_id = %s AND season_id = %s"
        val_check_saved = (int(self.id), int(self.season_id))
        mycursor = mydb.cursor()
        mycursor.execute(sql_check_saved, val_check_saved)
        id_tournament = mycursor.fetchall()
        mycursor.close()
        if len(id_tournament) == 0:
            return None
        else:
            return id_tournament[0][0]

    def save(self, mydb):
        id_tournament = self.get_id_db_tournament(mydb)
        if id_tournament == None:
            mycursor = mydb.cursor()
            sql = f"INSERT INTO tournament (tournament_id, season_id, country, year, name) VALUES (%s, %s, %s, %s, %s)"
            val = (int(self.id), int(self.season_id), self.country, int(self.year), self.name)
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
        self.id_tournament_db = id_tournament
    
    def save_standing(self, mydb):
        sql_check_exists = f"SELECT * FROM standing WHERE id_tournament = %s AND id_season = %s"
        val_check_exists = (int(self.id), int(self.season_id))
        mycursor = mydb.cursor()
        mycursor.execute(sql_check_exists, val_check_exists)
        exists = mycursor.fetchall()
        mycursor.close()
        for index, row in self.standing.iterrows():
            if len(exists) > 0:
                sql = f"UPDATE standing SET position = %s, points = %s, matches = %s WHERE id_tournament = %s AND id_season = %s AND id_team = %s"
                val = (int(row['position']), int(row['points']), int(row['matches']), int(self.id), int(self.season_id), int(row['id']))
            else:
                sql = f"INSERT INTO standing (id_tournament, id_season, id_team, position, points, matches) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (int(self.id), int(self.season_id), int(row['id']), int(row['position']), int(row['points']), int(row['matches']))
            mycursor = mydb.cursor()
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
            
    def save_teams_stats(self, mydb):
        sql = "INSERT INTO teams_stats_match (id_match, id_team, field, period, accurateCross, accurateLongBalls, accuratePasses, accurateThroughBall, aerialDuelsPercentage, ballPossession, ballRecovery, bigChanceCreated, bigChanceMissed, bigChanceScored, blockedScoringAttempt, cornerKicks, dispossessed, diveSaves, dribblesPercentage, duelWonPercent, errorsLeadToGoal, errorsLeadToShot, expectedGoals, finalThirdEntries, finalThirdPhaseStatistic, fouledFinalThird, fouls, freeKicks, goalKicks, goalkeeperSaves, goals, goalsPrevented, groundDuelsPercentage, highClaims, hitWoodwork, interceptionWon, offsides, passes, punches, redCards, shotsOffGoal, shotsOnGoal, throwIns, totalClearance, totalShotsInsideBox, totalShotsOnGoal, totalShotsOutsideBox, totalTackle, touchesInOppBox, wonTacklePercent, yellowCards) VALUES\
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = list()
        for id_jogo, jogo in self.jogos.items():
            if 'teams_stats' in jogo.__dict__:
                for id_team, team_stats_all in jogo.teams_stats.items():
                    for period in ['ALL', '1ST', '2ND']:
                        team_stats = team_stats_all[period]
                        val_i = [team_stats_all['id_event'], id_team, team_stats_all['field'], period]
                        vars_int = ['accurateCross', 'accurateLongBalls', 'accuratePasses', 'accurateThroughBall',
                        'aerialDuelsPercentage', 'ballPossession', 'ballRecovery', 'bigChanceCreated', 'bigChanceMissed',
                        'bigChanceScored', 'blockedScoringAttempt', 'cornerKicks', 'dispossessed', 'diveSaves',
                        'dribblesPercentage', 'duelWonPercent', 'errorsLeadToGoal', 'errorsLeadToShot', 'expectedGoals', 
                        'finalThirdEntries', 'finalThirdPhaseStatistic', 'fouledFinalThird', 'fouls', 'freeKicks', 'goalKicks', 
                        'goalkeeperSaves', 'goals', 'goalsPrevented', 'groundDuelsPercentage', 'highClaims', 'hitWoodwork', 
                        'interceptionWon', 'offsides', 'passes', 'punches', 'redCards', 'shotsOffGoal', 'shotsOnGoal', 'throwIns',
                            'totalClearance', 'totalShotsInsideBox', 'totalShotsOnGoal', 'totalShotsOutsideBox', 'totalTackle',
                            'touchesInOppBox', 'wonTacklePercent', 'yellowCards']        
                        for var in vars_int:
                            if var in team_stats.keys():
                                if team_stats[var] != None:
                                    team_stats[var] = float(team_stats[var])
                            else:
                                team_stats[var] = None
                            val_i.append(team_stats[var])
                        val.append(val_i)
        mycursor = mydb.cursor()
        mycursor.executemany(sql, val)
        mydb.commit()
        mycursor.close()
    
    def save_players_stats(self, mydb):
        sql = "INSERT INTO players_stats_match (id_match, id_team, id_player, field, accurateCross, accurateKeeperSweeper, accurateLongBalls, accuratePass, aerialLost, aerialWon, bigChanceCreated, bigChanceMissed, blockedScoringAttempt, challengeLost, clearanceOffLine, dispossessed, duelLost, duelWon, errorLeadToAGoal, errorLeadToAShot, expectedAssists, expectedGoals, fouls, goalAssist, goals, goalsPrevented, goodHighClaim, hitWoodwork, interceptionWon, keyPass, lastManTackle, minutesPlayed, onTargetScoringAttempt, outfielderBlock, ownGoals, penaltyConceded, penaltyMiss, penaltySave, penaltyWon, possessionLostCtrl, punches, rating, savedShotsFromInsideTheBox, saves, shotOffTarget, totalClearance, totalContest, totalCross, totalKeeperSweeper, totalLongBalls, totalOffside, totalPass, totalTackle, touches, wasFouled, wonContest) VALUES\
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
        val = list()
        for id_jogo, jogo in self.jogos.items():
            if 'teams_stats' in jogo.__dict__:
                for id_player, player_stats in jogo.players_statistics.items():
                    if player_stats['id_team'] == jogo.home_team.id:
                        field = 'home'
                    else:
                        field = 'away'
                    val_i = [player_stats['id_event'], player_stats['id_team'], id_player, field]
                    vars_int = ['accurateCross', 'accurateKeeperSweeper', 'accurateLongBalls', 'accuratePass', 'aerialLost',
                        'aerialWon', 'bigChanceCreated', 'bigChanceMissed', 'blockedScoringAttempt', 'challengeLost',
                        'clearanceOffLine', 'dispossessed', 'duelLost', 'duelWon', 'errorLeadToAGoal', 'errorLeadToAShot',
                        'expectedAssists', 'expectedGoals', 'fouls', 'goalAssist', 'goals', 'goalsPrevented', 'goodHighClaim',
                        'hitWoodwork', 'interceptionWon', 'keyPass', 'lastManTackle', 'minutesPlayed', 'onTargetScoringAttempt',
                        'outfielderBlock', 'ownGoals', 'penaltyConceded', 'penaltyMiss', 'penaltySave', 'penaltyWon',
                        'possessionLostCtrl', 'punches', 'rating', 'savedShotsFromInsideTheBox', 'saves', 'shotOffTarget',
                        'totalClearance', 'totalContest', 'totalCross', 'totalKeeperSweeper', 'totalLongBalls', 'totalOffside',
                        'totalPass', 'totalTackle', 'touches', 'wasFouled', 'wonContest'] 
                        
                    for var in vars_int:
                        if var in player_stats.keys():
                            if player_stats[var] != None:
                                player_stats[var] = float(player_stats[var])
                        else:
                            player_stats[var] = None
                        val_i.append(player_stats[var])
                    val.append(val_i)
        mycursor = mydb.cursor()
        mycursor.executemany(sql, val)
        mydb.commit()
        mycursor.close()
    
    def save_shotmap_match(self, mydb):
        sql = "INSERT INTO shots_match (id_match, id_team, id_player, field, shotType, goalType, xg, xgot, situation, bodypart, playerCoordinates, inBox, goalMouthLocation, time, time_seconds, period, score_after_goal, goal_to_ahead_score, goal_to_open_score, goal_to_tie, goal_winning, goal_to_save_lose) VALUES\
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = list()
        for id_jogo, jogo in self.jogos.items():
            if 'shotmap_info' in jogo.__dict__:
                for key, shot in jogo.shotmap_info.items():
                    if shot['id_team'] == jogo.home_team.id:
                        field = 'home'
                    else:
                        field = 'away'
                    val_i = [jogo.id, shot['id_team'], shot['id'], field]
                    vars = ['shotType', 'goalType', 'xg', 'xgot', 'situation', 'bodypart', 'playerCoordinates', 'inBox', 'goalMouthLocation', 'time', 'time_seconds', 'period', 'score_after_goal', 'goal_to_ahead_score', 'goal_to_open_score', 'goal_to_tie', 'goal_winning', 'goal_to_save_lose']
                    vars_float_or_int = ['xg', 'xgot', 'time', 'time_seconds', 'score_after_goal']
                    vars_coordinates = ['playerCoordinates']
                    for var in vars:
                        if var in shot.keys() and shot[var] != None:
                            if var in vars_float_or_int:
                                val_i.append(float(shot[var]))
                            elif var in vars_coordinates:
                                val_i.append(json.dumps(shot[var]))
                            else:
                                val_i.append(shot[var])
                        else:
                            val_i.append(None)
                    val.append(val_i)
        mycursor = mydb.cursor()
        mycursor.executemany(sql, val)
        mydb.commit()
        mycursor.close()
        
    def save_goals(self, mydb):
        sql = "INSERT INTO goal_match (id_match, scoreHome, scoreAway, scoreHome1st, scoreAway1st, scoreHome2nd, scoreAway2nd)\
            VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = list()
        for id_jogo, jogo in self.jogos.items():
            if 'goals_info' in jogo.__dict__:
                goals_info = jogo.goals_info
                val_i = [jogo.id, goals_info['ALL']['home'], goals_info['ALL']['away'], goals_info['1ST']['home'], goals_info['1ST']['away'], goals_info['2ND']['home'], goals_info['2ND']['away']]
                val.append(val_i)
        mycursor = mydb.cursor()
        mycursor.executemany(sql, val)
        mydb.commit()
        mycursor.close()
        

    def save_all(self, mydb):
        print('Salvando informações do torneio...')
        self.save(mydb)
        print('Salvando informações dos times...')
        for id_team, team in self.teams.items():
            team.save(mydb)
        print('Salvando informações dos jogos...')
        for id_jogo, jogo in self.jogos.items():
            jogo.save(mydb)
        print('Salvando informações dos jogadores...')
        for id_player, player in self.players.items():
            player.save(mydb)
        print('Salvando informações dos técnicos...')
        for id_manager, manager in self.managers.items():
            manager.save(mydb)
        print('Salvando informações dos árbitros...')
        for id_referee, referee in self.referees.items():
            referee.save(mydb)
        print('Salvando informações dos standings...')
        self.save_standing(mydb)
        print('Salvando informações das estatísticas dos times...')
        self.save_teams_stats(mydb)
        print('Salvando informações das estatísticas dos jogadores...')
        self.save_players_stats(mydb)  
        print('Salvando informações do shotmap...')
        self.save_shotmap_match(mydb)
        print('Salvando informações dos gols...')
        self.save_goals(mydb)

    def __str__(self) -> str:
        return f'Tournament: {self.name} - Country: {self.country} - Year: {self.year}'