import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore
from SQLconfig.config_mysql import mydb

class Player:
    def __init__(self, id):
        self.id = id

    def get_info_players(self):
        url = get_api_url() + f"player/{self.id}"
        dados_players = read_api_sofascore(url, selenium=False)
        dados_players = dados_players['player']
        self.name = dados_players['name']
        self.shortName = dados_players['shortName']
        self.teamId = dados_players['team']['id']
        self.position = dados_players['position']

        if 'height' in dados_players:
            self.height = dados_players['height']
        else:
            self.height = None

        if 'jerseyNumber' in dados_players:
            self.jerseyNumber = dados_players['jerseyNumber']
        else:
            self.jerseyNumber = None

        if 'dateOfBirthTimestamp' in dados_players:
            date_of_birth = datetime.fromtimestamp(dados_players['dateOfBirthTimestamp'])
            current_date = datetime.now()
            interval_years = current_date - date_of_birth
            interval_years = current_date - date_of_birth
            self.age = int(interval_years.days/365)
        else:
            self.age = None
        
        if 'preferredFoot' in dados_players:
            self.preferredFoot = dados_players['preferredFoot']
        else:
            self.preferredFoot = None
        
    def save(self, mydb):
        mycursor = mydb.cursor()
        sql = "INSERT INTO player (id, id_team, name, shortName, position, height, jerseyNumber, age, preferredFoot) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        vars_int = ['id', 'teamId', 'height', 'jerseyNumber', 'age']
        for var in vars_int:
            if self.__dict__[var] != None:
                self.__dict__[var] = int(self.__dict__[var])
        val = (self.id, self.teamId, self.name, self.shortName, self.position, self.height, self.jerseyNumber, self.age, self.preferredFoot)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        
    def __str__(self):
        return f"Player: {self.shortName} - ID: {self.id} - Team ID: {self.teamId} - Position: {self.position}"